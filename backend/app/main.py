import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ReviveException
from app.database.session import init_db
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing REVIVE backend application...")
    await init_db()
    logger.info("REVIVE backend ready for revenue recovery operations.")
    yield
    logger.info("Shutting down REVIVE backend.")


app = FastAPI(
    title="REVIVE — Autonomous AI Revenue Recovery",
    description="Autonomous revenue recovery orchestration layer combining contextual diagnosis, merchant policies, bounded execution, and measurable outcomes.",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Assigns or propagates X-Correlation-ID for distributed tracing and auditability."""
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    
    start_time = time.time()
    response: Response = await call_next(request)
    latency_ms = int((time.time() - start_time) * 1000)
    
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time-Ms"] = str(latency_ms)
    return response


@app.exception_handler(ReviveException)
async def revive_exception_handler(request: Request, exc: ReviveException):
    logger.warning(f"Operational error: [{exc.code}] {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": exc.code,
            "message": exc.message,
            "correlation_id": getattr(request.state, "correlation_id", None)
        }
    )


# Mount API Router
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": settings.INTEGRATION_MODE,
        "documentation": "/docs"
    }
