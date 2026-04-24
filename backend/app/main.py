import time
import logging
from collections import defaultdict
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from anthropic import AsyncAnthropic

from .config import settings
from .dependencies import get_supabase_client
from ml.predict import PredictionService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Middlewares ---

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {process_time:.4f}s"
        )
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # In-memory store: { ip: [timestamp1, timestamp2, ...] }
        self.request_counts = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Clean up old timestamps
        self.request_counts[client_ip] = [
            ts for ts in self.request_counts[client_ip] 
            if now - ts < self.window_seconds
        ]
        
        if len(self.request_counts[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "Too Many Requests", "detail": "Rate limit exceeded"}
            )
            
        self.request_counts[client_ip].append(now)
        return await call_next(request)

# --- Lifecycle Events ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load ML models
    logger.info("Loading ML models into app.state...")
    try:
        app.state.prediction_service = PredictionService()
        logger.info("ML models loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load ML models: {e}")
        app.state.prediction_service = None
        
    yield
    # Shutdown events can go here

# --- App Initialization ---

app = FastAPI(
    title="FinSight AI API",
    description="Backend API for financial insights and ML predictions",
    version="1.0.0",
    lifespan=lifespan
)

# Add Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# --- Exception Handlers ---

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else "An unexpected error occurred.",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    )

# --- Routers ---
# Placeholder for when we add actual routers
# from .routers import auth, assessments, etc...
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

# --- Health Check ---

@app.get("/api/health")
async def health_check(request: Request):
    health_status = {
        "status": "ok",
        "version": "1.0.0",
        "service": "finsight-ai-backend",
        "components": {
            "database": "unknown",
            "ml_models": "unknown",
            "llm": "unknown"
        }
    }
    
    # Check ML Models
    if hasattr(request.app.state, "prediction_service") and request.app.state.prediction_service is not None:
        if 'model' in request.app.state.prediction_service.artifacts:
            health_status["components"]["ml_models"] = "loaded"
        else:
            health_status["components"]["ml_models"] = "error"
            health_status["status"] = "degraded"
    else:
        health_status["components"]["ml_models"] = "not_initialized"
        health_status["status"] = "degraded"
        
    # Check Database (Supabase)
    try:
        sb_client = await get_supabase_client()
        # Simple query to check connection
        # Supabase API doesn't have a direct 'ping', so we just try to read a row or rely on client init
        # Note: We won't actually hit the DB here to avoid latency on every health check unless necessary, 
        # but the client creation confirms the URL/Key are parsed.
        health_status["components"]["database"] = "configured"
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
        
    # Check LLM (Anthropic)
    try:
        anthropic = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        # We don't make an API call to save costs, just verify the client initializes
        health_status["components"]["llm"] = "configured"
    except Exception as e:
        health_status["components"]["llm"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    return JSONResponse(
        status_code=200 if health_status["status"] == "ok" else 503,
        content=health_status
    )
