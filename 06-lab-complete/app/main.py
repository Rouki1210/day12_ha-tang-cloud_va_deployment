import json
import logging
import signal
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.auth import verify_api_key
from app.config import settings
from app.storage import storage
from utils.mock_llm import ask as mock_ask


logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)

START_TIME = time.time()
is_ready = False


def handle_sigterm(signum, _frame):
    logger.info(json.dumps({"event": "signal", "signum": signum}))


signal.signal(signal.SIGTERM, handle_sigterm)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    session_id: str | None = None


class AskResponse(BaseModel):
    session_id: str
    answer: str
    turn: int
    model: str


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global is_ready
    logger.info(json.dumps({"event": "startup", "app": settings.app_name}))
    is_ready = storage.ping()
    yield
    is_ready = False
    logger.info(json.dumps({"event": "shutdown"}))


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "X-API-Key"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    started = time.time()
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    logger.info(json.dumps({
        "event": "request",
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round((time.time() - started) * 1000, 1),
    }))
    return response


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready")
def ready():
    if not is_ready or not storage.ping():
        raise HTTPException(status_code=503, detail="Storage is not ready")
    return {"ready": True, "storage": storage.backend}


@app.post("/ask", response_model=AskResponse)
def ask_agent(body: AskRequest, api_key: str = Depends(verify_api_key)):
    user_id = api_key[:8]
    storage.check_rate_limit(user_id, settings.rate_limit_per_minute)

    estimated_cost = max(0.000001, len(body.question.split()) * 0.000001)
    storage.check_and_record_budget(
        user_id,
        estimated_cost,
        settings.monthly_budget_usd,
    )

    session_id = body.session_id or str(uuid.uuid4())
    storage.append_message(session_id, "user", body.question)
    answer = mock_ask(body.question)
    history = storage.append_message(session_id, "assistant", answer)

    logger.info(json.dumps({
        "event": "agent_answer",
        "session_id": session_id,
        "question_length": len(body.question),
    }))

    return AskResponse(
        session_id=session_id,
        answer=answer,
        turn=len([item for item in history if item["role"] == "user"]),
        model=settings.llm_model,
    )


@app.get("/history/{session_id}")
def get_history(session_id: str, _api_key: str = Depends(verify_api_key)):
    history = storage.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "messages": history}


@app.delete("/history/{session_id}")
def delete_history(session_id: str, _api_key: str = Depends(verify_api_key)):
    storage.delete_history(session_id)
    return {"deleted": session_id}


@app.get("/metrics")
def metrics(api_key: str = Depends(verify_api_key)):
    user_id = api_key[:8]
    return {
        "storage": storage.backend,
        "monthly_cost_usd": storage.get_monthly_cost(user_id),
        "monthly_budget_usd": settings.monthly_budget_usd,
        "rate_limit_per_minute": settings.rate_limit_per_minute,
    }
