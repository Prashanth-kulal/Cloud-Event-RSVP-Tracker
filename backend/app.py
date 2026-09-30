"""
Real-Time Cloud-Based Event Planning & RSVP Tracker
FastAPI Application Entry Point

Architecture:
  - Routers: auth, events, rsvp, waitlist, announcements, notifications, analytics
  - Real-time: WebSocket (local) | Firestore listeners (cloud)
  - Database: SQLite (local) | Firestore (cloud)
  - Auth: JWT (local) | Firebase Auth (cloud)
"""
import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Ensure project root is on sys.path so backend.* and realtime.* are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.database import init_db
from backend.routes import auth, events, rsvp, waitlist, announcements, notifications, analytics, websocket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    await init_db()
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-Time Cloud-Based Event Planning & RSVP Tracker API",
    lifespan=lifespan
)

# CORS — allow React dev server and production frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Global Error Handlers ────────────────────────────────────────────────────

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = errors[0].get("msg") if errors else "Validation error"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "message": msg, "errors": errors}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "An internal server error occurred."}
    )


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["health"])
async def health():
    return {"status": "ok", "version": settings.APP_VERSION, "app": settings.APP_NAME}


# ─── Register Routers ─────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(rsvp.router)
app.include_router(waitlist.router)
app.include_router(announcements.router)
app.include_router(notifications.router)
app.include_router(analytics.router)
app.include_router(websocket.router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port, reload=True)
