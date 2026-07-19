"""
HEI HTTP API (FastAPI)

Ready to sit behind any API Gateway (Kong, AWS API Gateway, Nginx, Cloudflare, etc.)

Run:
    uvicorn hei.api:app --host 0.0.0.0 --port 8000 --reload

Environment:
    OPENAI_API_KEY / HEI_API_KEY
    OPENAI_BASE_URL / HEI_BASE_URL
    HEI_MODEL
    HEI_API_TOKEN          - If set, requires Authorization: Bearer <token> or X-API-Key
    HEI_CORS_ORIGINS       - Comma-separated origins (default: *)
"""

from __future__ import annotations

import logging
import os
import time
from collections import defaultdict, deque
from typing import Deque, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from hei import HEI, HEIError, HEIValidationError
from hei.models import StrategyResult, ToneConfig

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("hei.api")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API_TOKEN = os.getenv("HEI_API_TOKEN", "").strip()
RATE_LIMIT = int(os.getenv("HEI_API_RATE_LIMIT", "120"))  # per minute
CORS_ORIGINS = [
    o.strip() for o in os.getenv("HEI_CORS_ORIGINS", "*").split(",") if o.strip()
]

# ---------------------------------------------------------------------------
# Rate limiter (simple in-memory)
# ---------------------------------------------------------------------------

_rate_buckets: Dict[str, Deque[float]] = defaultdict(deque)


def check_rate_limit(key: str) -> None:
    now = time.time()
    window = 60.0
    bucket = _rate_buckets[key]

    while bucket and bucket[0] <= now - window:
        bucket.popleft()

    if len(bucket) >= RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {RATE_LIMIT} requests per minute.",
        )
    bucket.append(now)


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------

async def verify_auth(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> str:
    """If HEI_API_TOKEN is set, require Bearer token or X-API-Key."""
    if not API_TOKEN:
        return "anonymous"

    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_api_key:
        token = x_api_key.strip()

    if not token or token != API_TOKEN:
        logger.warning("Unauthorized request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = Field(None, max_length=128)


class EmotionRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class IntentRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    emotion_context: Optional[str] = None


class EvaluateRequest(BaseModel):
    original_message: str = Field(..., min_length=1, max_length=4000)
    generated_response: str = Field(..., min_length=1, max_length=8000)
    strategy: dict


# ---------------------------------------------------------------------------
# App + HEI instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Human Emotion Intelligence (HEI) API",
    description="Conversation Intelligence Layer for LLMs. Detect emotion, intent, plan strategy, evaluate responses.",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_hei: Optional[HEI] = None


def get_hei() -> HEI:
    global _hei
    if _hei is None:
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("HEI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("HEI_BASE_URL")
        model = os.getenv("HEI_MODEL", "gpt-4o-mini")

        if not api_key:
            raise RuntimeError("OPENAI_API_KEY or HEI_API_KEY is required")

        _hei = HEI(api_key=api_key, base_url=base_url, model=model)
        logger.info("HEI instance ready (model=%s)", model)
    return _hei


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "hei",
        "version": "0.2.0",
        "auth_required": bool(API_TOKEN),
    }


@app.post("/v1/analyze")
async def analyze(
    body: AnalyzeRequest,
    request: Request,
    auth_key: str = Depends(verify_auth),
):
    check_rate_limit(auth_key)

    try:
        hei = get_hei()
        result = hei.analyze(body.message, session_id=body.session_id)

        return {
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
            "model_used": result.model_used,
        }
    except HEIValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HEIError as e:
        logger.error("analyze failed: %s", e)
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.exception("analyze unexpected error")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/v1/emotion")
async def detect_emotion(
    body: EmotionRequest,
    auth_key: str = Depends(verify_auth),
):
    check_rate_limit(auth_key)

    try:
        hei = get_hei()
        emotion = hei.emotion_analyzer.analyze(body.message)
        return {
            "primary": emotion.primary.value,
            "secondary": emotion.secondary.value if emotion.secondary else None,
            "hidden": emotion.hidden.value if emotion.hidden else None,
            "intensity": emotion.intensity,
            "confidence": emotion.confidence,
            "reasoning": emotion.reasoning,
        }
    except HEIValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("emotion error")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/v1/intent")
async def detect_intent(
    body: IntentRequest,
    auth_key: str = Depends(verify_auth),
):
    check_rate_limit(auth_key)

    try:
        hei = get_hei()
        intent = hei.intent_detector.detect(body.message, body.emotion_context)
        return {
            "primary_intent": intent.primary_intent.value,
            "secondary_intent": intent.secondary_intent.value if intent.secondary_intent else None,
            "confidence": intent.confidence,
            "reasoning": intent.reasoning,
        }
    except Exception as e:
        logger.exception("intent error")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/v1/mood-shift/{session_id}")
async def mood_shift(
    session_id: str,
    auth_key: str = Depends(verify_auth),
):
    check_rate_limit(auth_key)

    if not session_id or len(session_id) > 128:
        raise HTTPException(status_code=400, detail="Invalid session_id")

    hei = get_hei()
    shift = hei.get_mood_shift(session_id)

    return {
        "shift_type": shift.shift_type.value,
        "from_emotion": shift.from_emotion,
        "to_emotion": shift.to_emotion,
        "from_intensity": shift.from_intensity,
        "to_intensity": shift.to_intensity,
        "summary": shift.summary,
    }


@app.post("/v1/evaluate")
async def evaluate(
    body: EvaluateRequest,
    auth_key: str = Depends(verify_auth),
):
    check_rate_limit(auth_key)

    try:
        tone_data = body.strategy.get("tone", {})
        strategy = StrategyResult(
            current_emotion=body.strategy.get("current_emotion", ""),
            target_outcome=body.strategy.get("target_outcome", ""),
            recommended_strategy=body.strategy.get("recommended_strategy", ""),
            tone=ToneConfig(**tone_data) if tone_data else ToneConfig(),
            things_to_avoid=body.strategy.get("things_to_avoid", []),
            suggested_approach=body.strategy.get("suggested_approach", ""),
            reasoning=body.strategy.get("reasoning", ""),
        )

        hei = get_hei()
        evaluation = hei.evaluate_response(
            body.original_message,
            body.generated_response,
            strategy,
        )

        return {
            "empathy_score": evaluation.empathy_score,
            "human_likeness": evaluation.human_likeness,
            "safety_score": evaluation.safety_score,
            "clarity_score": evaluation.clarity_score,
            "overall_score": evaluation.overall_score,
            "feedback": evaluation.feedback,
            "should_rewrite": evaluation.should_rewrite,
            "rewrite_suggestion": evaluation.rewrite_suggestion,
        }
    except Exception as e:
        logger.exception("evaluate error")
        raise HTTPException(status_code=500, detail="Internal server error")


# ---------------------------------------------------------------------------
# Local dev entry
# ---------------------------------------------------------------------------

def main():
    import uvicorn

    host = os.getenv("HEI_HOST", "0.0.0.0")
    port = int(os.getenv("HEI_PORT", "8000"))
    logger.info("Starting HEI API on %s:%s (auth=%s)", host, port, "on" if API_TOKEN else "off")
    uvicorn.run("hei.api:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
