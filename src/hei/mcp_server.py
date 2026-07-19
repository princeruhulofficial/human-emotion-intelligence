"""
HEI MCP Server (Security Hardened)

Exposes Human Emotion Intelligence as Model Context Protocol tools.
Compatible with Claude Desktop, Cursor, Windsurf, and other MCP clients.

Security features:
- Optional shared-secret token authentication
- Basic in-memory rate limiting
- Stricter input length limits
- Structured logging

Run:
    python -m hei.mcp_server

Environment variables:
    OPENAI_API_KEY / HEI_API_KEY   - Required
    OPENAI_BASE_URL / HEI_BASE_URL - Optional
    HEI_MODEL                      - Optional (default: gpt-4o-mini)
    HEI_MCP_TOKEN                  - Optional shared secret. If set, every tool call must include it.
    HEI_MCP_RATE_LIMIT             - Max calls per minute per token/IP (default: 60)
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from collections import defaultdict, deque
from typing import Any, Deque, Dict, Optional

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("hei.mcp")

# ---------------------------------------------------------------------------
# Official MCP SDK
# ---------------------------------------------------------------------------

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

from hei import HEI, HEIValidationError, HEIError
from hei.models import StrategyResult, ToneConfig

# ---------------------------------------------------------------------------
# Security configuration
# ---------------------------------------------------------------------------

MAX_MESSAGE_LENGTH = 4000          # Stricter than core HEI limit for MCP
MAX_SESSION_ID_LENGTH = 128
DEFAULT_RATE_LIMIT = 60            # calls per minute

MCP_TOKEN = os.getenv("HEI_MCP_TOKEN", "").strip()
RATE_LIMIT = int(os.getenv("HEI_MCP_RATE_LIMIT", DEFAULT_RATE_LIMIT))

# In-memory rate limiter: key -> deque of timestamps
_rate_buckets: Dict[str, Deque[float]] = defaultdict(deque)


def _check_rate_limit(key: str) -> None:
    """Simple sliding-window rate limiter."""
    now = time.time()
    window = 60.0  # 1 minute

    bucket = _rate_buckets[key]

    # Drop old timestamps
    while bucket and bucket[0] <= now - window:
        bucket.popleft()

    if len(bucket) >= RATE_LIMIT:
        logger.warning("Rate limit exceeded for key=%s (limit=%s/min)", key[:12], RATE_LIMIT)
        raise PermissionError(
            f"Rate limit exceeded. Max {RATE_LIMIT} calls per minute. Try again later."
        )

    bucket.append(now)


def _verify_token(token: str = "") -> None:
    """If HEI_MCP_TOKEN is set, require it on every call."""
    if not MCP_TOKEN:
        return  # auth disabled

    if not token or token.strip() != MCP_TOKEN:
        logger.warning("Invalid or missing MCP token")
        raise PermissionError("Invalid or missing authentication token.")


def _validate_message(message: str) -> str:
    if message is None or not isinstance(message, str):
        raise ValueError("message must be a non-empty string")

    cleaned = message.strip()
    if not cleaned:
        raise ValueError("message cannot be empty")

    if len(cleaned) > MAX_MESSAGE_LENGTH:
        raise ValueError(
            f"message too long ({len(cleaned)} chars). Maximum allowed: {MAX_MESSAGE_LENGTH}"
        )

    return cleaned


def _validate_session_id(session_id: str) -> Optional[str]:
    if not session_id or not session_id.strip():
        return None

    sid = session_id.strip()
    if len(sid) > MAX_SESSION_ID_LENGTH:
        raise ValueError(f"session_id too long. Maximum: {MAX_SESSION_ID_LENGTH} chars")

    # Very basic sanitation
    if any(c in sid for c in ["\n", "\r", "\0"]):
        raise ValueError("session_id contains invalid characters")

    return sid


# ---------------------------------------------------------------------------
# Server + HEI instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "hei",
    description=(
        "Human Emotion Intelligence (HEI) - Conversation Intelligence Layer for AI. "
        "Detects emotion, intent, plans response strategy, and evaluates replies."
    ),
)

_hei: Optional[HEI] = None


def get_hei() -> HEI:
    global _hei
    if _hei is None:
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("HEI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("HEI_BASE_URL")
        model = os.getenv("HEI_MODEL", "gpt-4o-mini")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY or HEI_API_KEY environment variable is required."
            )

        _hei = HEI(api_key=api_key, base_url=base_url, model=model)
        logger.info("HEI instance created (model=%s)", model)
    return _hei


def _secure_gate(token: str = "", rate_key: str = "default") -> None:
    """Run authentication + rate limiting before any tool logic."""
    _verify_token(token)
    _check_rate_limit(rate_key or "default")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def hei_analyze(
    message: str,
    session_id: str = "",
    token: str = "",
) -> str:
    """
    Full HEI analysis pipeline: Emotion Detection + Intent Detection + Response Strategy.

    Use this when you need to understand how a user is feeling and how you should respond.

    Args:
        message: The user's message to analyze.
        session_id: Optional session ID for emotional memory across turns.
        token: Optional shared secret (required if HEI_MCP_TOKEN is set on the server).

    Returns:
        JSON with emotion, intent, and strategy.
    """
    try:
        _secure_gate(token=token, rate_key=token or "anon")
        message = _validate_message(message)
        sid = _validate_session_id(session_id)

        hei = get_hei()
        result = hei.analyze(message, session_id=sid)

        payload = {
            "emotion": {
                "primary": result.emotion.primary.value,
                "secondary": result.emotion.secondary.value if result.emotion.secondary else None,
                "hidden": result.emotion.hidden.value if result.emotion.hidden else None,
                "intensity": result.emotion.intensity,
                "confidence": result.emotion.confidence,
                "reasoning": result.emotion.reasoning,
            },
            "intent": {
                "primary": result.intent.primary_intent.value,
                "secondary": result.intent.secondary_intent.value if result.intent.secondary_intent else None,
                "confidence": result.intent.confidence,
                "reasoning": result.intent.reasoning,
            },
            "strategy": {
                "current_emotion": result.strategy.current_emotion,
                "target_outcome": result.strategy.target_outcome,
                "recommended_strategy": result.strategy.recommended_strategy,
                "tone": result.strategy.tone.model_dump(),
                "things_to_avoid": result.strategy.things_to_avoid,
                "suggested_approach": result.strategy.suggested_approach,
                "reasoning": result.strategy.reasoning,
            },
        }

        logger.info(
            "hei_analyze ok | session=%s | emotion=%s | intent=%s",
            sid or "-",
            result.emotion.primary.value,
            result.intent.primary_intent.value,
        )
        return json.dumps(payload, indent=2, ensure_ascii=False)

    except (PermissionError, ValueError, HEIValidationError) as e:
        logger.warning("hei_analyze rejected: %s", e)
        return json.dumps({"error": str(e), "type": type(e).__name__})
    except HEIError as e:
        logger.error("hei_analyze failed: %s", e)
        return json.dumps({"error": str(e), "type": "HEIError"})
    except Exception as e:
        logger.exception("hei_analyze unexpected error")
        return json.dumps({"error": "Internal server error", "type": "InternalError"})


@mcp.tool()
def hei_detect_emotion(message: str, token: str = "") -> str:
    """
    Detect the emotional state of a message (primary, secondary, hidden, intensity).

    Args:
        message: The text to analyze.
        token: Optional shared secret (required if HEI_MCP_TOKEN is set).

    Returns:
        JSON with emotion analysis.
    """
    try:
        _secure_gate(token=token, rate_key=token or "anon")
        message = _validate_message(message)

        hei = get_hei()
        emotion = hei.emotion_analyzer.analyze(message)

        payload = {
            "primary": emotion.primary.value,
            "secondary": emotion.secondary.value if emotion.secondary else None,
            "hidden": emotion.hidden.value if emotion.hidden else None,
            "intensity": emotion.intensity,
            "confidence": emotion.confidence,
            "reasoning": emotion.reasoning,
        }
        logger.info("hei_detect_emotion ok | primary=%s", emotion.primary.value)
        return json.dumps(payload, indent=2, ensure_ascii=False)

    except (PermissionError, ValueError, HEIValidationError) as e:
        return json.dumps({"error": str(e), "type": type(e).__name__})
    except Exception as e:
        logger.exception("hei_detect_emotion error")
        return json.dumps({"error": "Internal server error", "type": "InternalError"})


@mcp.tool()
def hei_detect_intent(message: str, emotion_context: str = "", token: str = "") -> str:
    """
    Detect the emotional intent behind a message.

    Args:
        message: The user's message.
        emotion_context: Optional previous emotion context.
        token: Optional shared secret.

    Returns:
        JSON with intent analysis.
    """
    try:
        _secure_gate(token=token, rate_key=token or "anon")
        message = _validate_message(message)

        hei = get_hei()
        ctx = emotion_context.strip() or None
        intent = hei.intent_detector.detect(message, ctx)

        payload = {
            "primary_intent": intent.primary_intent.value,
            "secondary_intent": intent.secondary_intent.value if intent.secondary_intent else None,
            "confidence": intent.confidence,
            "reasoning": intent.reasoning,
        }
        logger.info("hei_detect_intent ok | intent=%s", intent.primary_intent.value)
        return json.dumps(payload, indent=2, ensure_ascii=False)

    except (PermissionError, ValueError, HEIValidationError) as e:
        return json.dumps({"error": str(e), "type": type(e).__name__})
    except Exception as e:
        logger.exception("hei_detect_intent error")
        return json.dumps({"error": "Internal server error", "type": "InternalError"})


@mcp.tool()
def hei_get_mood_shift(session_id: str, token: str = "") -> str:
    """
    Detect if the user's mood has shifted in the current session.

    Args:
        session_id: The session identifier used in previous hei_analyze calls.
        token: Optional shared secret.

    Returns:
        JSON describing the mood shift.
    """
    try:
        _secure_gate(token=token, rate_key=token or "anon")
        sid = _validate_session_id(session_id)
        if not sid:
            raise ValueError("session_id is required")

        hei = get_hei()
        shift = hei.get_mood_shift(sid)

        payload = {
            "shift_type": shift.shift_type.value,
            "from_emotion": shift.from_emotion,
            "to_emotion": shift.to_emotion,
            "from_intensity": shift.from_intensity,
            "to_intensity": shift.to_intensity,
            "summary": shift.summary,
        }
        logger.info("hei_get_mood_shift ok | session=%s | type=%s", sid, shift.shift_type.value)
        return json.dumps(payload, indent=2, ensure_ascii=False)

    except (PermissionError, ValueError) as e:
        return json.dumps({"error": str(e), "type": type(e).__name__})
    except Exception as e:
        logger.exception("hei_get_mood_shift error")
        return json.dumps({"error": "Internal server error", "type": "InternalError"})


@mcp.tool()
def hei_evaluate_response(
    original_message: str,
    generated_response: str,
    strategy_json: str,
    token: str = "",
) -> str:
    """
    Evaluate how well a generated response follows the emotional strategy.

    Args:
        original_message: The user's original message.
        generated_response: The AI's reply to evaluate.
        strategy_json: The strategy object (as JSON string) from hei_analyze.
        token: Optional shared secret.

    Returns:
        JSON with scores and feedback.
    """
    try:
        _secure_gate(token=token, rate_key=token or "anon")
        original_message = _validate_message(original_message)

        if not generated_response or not generated_response.strip():
            raise ValueError("generated_response cannot be empty")
        if len(generated_response) > MAX_MESSAGE_LENGTH * 2:
            raise ValueError("generated_response too long")

        data = json.loads(strategy_json)
        tone_data = data.get("tone", {})
        strategy = StrategyResult(
            current_emotion=data.get("current_emotion", ""),
            target_outcome=data.get("target_outcome", ""),
            recommended_strategy=data.get("recommended_strategy", ""),
            tone=ToneConfig(**tone_data) if tone_data else ToneConfig(),
            things_to_avoid=data.get("things_to_avoid", []),
            suggested_approach=data.get("suggested_approach", ""),
            reasoning=data.get("reasoning", ""),
        )

        hei = get_hei()
        evaluation = hei.evaluate_response(original_message, generated_response, strategy)

        payload = {
            "empathy_score": evaluation.empathy_score,
            "human_likeness": evaluation.human_likeness,
            "safety_score": evaluation.safety_score,
            "clarity_score": evaluation.clarity_score,
            "overall_score": evaluation.overall_score,
            "feedback": evaluation.feedback,
            "should_rewrite": evaluation.should_rewrite,
            "rewrite_suggestion": evaluation.rewrite_suggestion,
        }
        logger.info(
            "hei_evaluate_response ok | overall=%.1f | rewrite=%s",
            evaluation.overall_score,
            evaluation.should_rewrite,
        )
        return json.dumps(payload, indent=2, ensure_ascii=False)

    except (PermissionError, ValueError, json.JSONDecodeError) as e:
        return json.dumps({"error": str(e), "type": type(e).__name__})
    except Exception as e:
        logger.exception("hei_evaluate_response error")
        return json.dumps({"error": "Internal server error", "type": "InternalError"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    auth_status = "ENABLED" if MCP_TOKEN else "DISABLED"
    logger.info(
        "Starting HEI MCP Server | auth=%s | rate_limit=%s/min | max_msg_len=%s",
        auth_status,
        RATE_LIMIT,
        MAX_MESSAGE_LENGTH,
    )
    mcp.run()


if __name__ == "__main__":
    main()
