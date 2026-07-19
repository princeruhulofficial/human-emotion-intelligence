"""
HEI MCP Server

Exposes Human Emotion Intelligence as Model Context Protocol tools.
Compatible with Claude Desktop, Cursor, Windsurf, and other MCP clients.

Run:
    python -m hei.mcp_server

Or with uvx / pipx after install.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Optional

# Official MCP SDK
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

from hei import HEI
from hei.models import StrategyResult, ToneConfig

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "hei",
    description="Human Emotion Intelligence (HEI) - Conversation Intelligence Layer for AI. Detects emotion, intent, plans response strategy, and evaluates replies.",
)

# Global HEI instance (lazy init)
_hei: Optional[HEI] = None


def get_hei() -> HEI:
    global _hei
    if _hei is None:
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("HEI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("HEI_BASE_URL")
        model = os.getenv("HEI_MODEL", "gpt-4o-mini")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY or HEI_API_KEY environment variable is required for HEI MCP server."
            )

        _hei = HEI(api_key=api_key, base_url=base_url, model=model)
    return _hei


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def hei_analyze(message: str, session_id: str = "") -> str:
    """
    Full HEI analysis pipeline: Emotion Detection + Intent Detection + Response Strategy.

    Use this when you need to understand how a user is feeling and how you should respond.

    Args:
        message: The user's message to analyze.
        session_id: Optional session ID for emotional memory across turns.

    Returns:
        JSON with emotion, intent, and strategy.
    """
    hei = get_hei()
    sid = session_id.strip() or None
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
    return json.dumps(payload, indent=2, ensure_ascii=False)


@mcp.tool()
def hei_detect_emotion(message: str) -> str:
    """
    Detect the emotional state of a message (primary, secondary, hidden, intensity).

    Args:
        message: The text to analyze.

    Returns:
        JSON with emotion analysis.
    """
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
    return json.dumps(payload, indent=2, ensure_ascii=False)


@mcp.tool()
def hei_detect_intent(message: str, emotion_context: str = "") -> str:
    """
    Detect the emotional intent behind a message (seeking comfort, venting, celebrating, etc.).

    Args:
        message: The user's message.
        emotion_context: Optional previous emotion context to improve accuracy.

    Returns:
        JSON with intent analysis.
    """
    hei = get_hei()
    ctx = emotion_context.strip() or None
    intent = hei.intent_detector.detect(message, ctx)

    payload = {
        "primary_intent": intent.primary_intent.value,
        "secondary_intent": intent.secondary_intent.value if intent.secondary_intent else None,
        "confidence": intent.confidence,
        "reasoning": intent.reasoning,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


@mcp.tool()
def hei_get_mood_shift(session_id: str) -> str:
    """
    Detect if the user's mood has shifted in the current session.

    Requires that previous turns were analyzed with the same session_id.

    Args:
        session_id: The session identifier used in previous hei_analyze calls.

    Returns:
        JSON describing the mood shift (or none).
    """
    hei = get_hei()
    shift = hei.get_mood_shift(session_id)

    payload = {
        "shift_type": shift.shift_type.value,
        "from_emotion": shift.from_emotion,
        "to_emotion": shift.to_emotion,
        "from_intensity": shift.from_intensity,
        "to_intensity": shift.to_intensity,
        "summary": shift.summary,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


@mcp.tool()
def hei_evaluate_response(
    original_message: str,
    generated_response: str,
    strategy_json: str,
) -> str:
    """
    Evaluate how well a generated response follows the emotional strategy and makes the user feel understood.

    Args:
        original_message: The user's original message.
        generated_response: The AI's reply to evaluate.
        strategy_json: The strategy object (as JSON string) returned by hei_analyze.

    Returns:
        JSON with scores and feedback.
    """
    hei = get_hei()

    try:
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
    except Exception as e:
        return json.dumps({"error": f"Invalid strategy_json: {e}"})

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
    return json.dumps(payload, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    mcp.run()


if __name__ == "__main__":
    main()
