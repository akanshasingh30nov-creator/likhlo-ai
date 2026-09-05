import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response

from likhlo_ai.config import settings
from likhlo_ai.database import init_db
from likhlo_ai.api import (
    transactions_router,
    voice_router,
    reminders_router,
    analytics_router,
    export_router
)

logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("likhlo_ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing LikhLo AI SQLite database...")
    init_db()
    logger.info("LikhLo AI application ready: Bhaiya, Likh Lo!")
    yield
    logger.info("LikhLo AI application shutting down.")


app = FastAPI(
    title=settings.app_name,
    description="LikhLo AI: Voice-First AI Khata & Ledger Copilot for 63M+ Micro-Merchants",
    version=settings.app_version,
    lifespan=lifespan
)

# Ensure tables are initialized on import
try:
    init_db()
except Exception as e:
    logger.warning(f"Database pre-init note: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please check voice input and retry."}
    )


# Register API Routers
app.include_router(transactions_router)
app.include_router(voice_router)
app.include_router(reminders_router)
app.include_router(analytics_router)
app.include_router(export_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "tagline": settings.app_tagline,
        "version": settings.app_version,
        "database": "sqlite_wal",
        "openai_configured": bool(settings.openai_api_key)
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    svg_icon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🎙️</text></svg>'
    return Response(content=svg_icon, media_type="image/svg+xml")


# Mount frontend static directory
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("likhlo_ai.server:app", host="127.0.0.1", port=8000, reload=True)
