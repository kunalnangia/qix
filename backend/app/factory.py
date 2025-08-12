# This file will contain the FastAPI app factory.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

import logging
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, APIRouter, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import API routers
from app.api.v1.routes import (
    test_cases,
    teams,
    environments,
    attachments,
    projects,
    comments,
    auth,
    executions,
    ai,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    A non-destructive lifespan manager for the FastAPI application.
    """
    logger.info("Application starting up...")
    # You can add any startup logic here, e.g., connecting to a database
    yield
    logger.info("Application shutting down...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title="IntelliTest AI Automation Platform",
        description="Enterprise-grade AI-powered test automation platform",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    origins = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "http://192.168.1.2:5175",
        "http://192.168.1.2:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,
    )

    # Exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(
            f"HTTP Exception: {exc.status_code} - {exc.detail} - Path: {request.url.path}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code,
                "path": request.url.path,
                "timestamp": datetime.utcnow().isoformat(),
            },
            headers=exc.headers if hasattr(exc, "headers") else None,
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(
            f"Unhandled Exception: {str(exc)} - Path: {request.url.path}"
        )
        logger.debug(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error": str(exc),
                "path": request.url.path,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    # API Routers
    api_router = APIRouter(prefix="/api")

    # Include all your routers here
    # This is still a bit messy, we will clean this up in the next step
    api_router.include_router(auth.router, tags=["Authentication"])
    api_router.include_router(projects.router, tags=["Projects"])
    api_router.include_router(test_cases.router, tags=["Test Cases"])
    api_router.include_router(teams.router, tags=["Teams"])
    api_router.include_router(environments.router, tags=["Environments"])
    api_router.include_router(attachments.router, tags=["Attachments"])
    api_router.include_router(comments.router, tags=["Comments"])
    api_router.include_router(executions.router, tags=["Executions"])
    api_router.include_router(ai.router, tags=["AI"])


    @api_router.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

    app.include_router(api_router)

    @app.get("/", tags=["Health"])
    async def root():
        return {
            "message": "Welcome to IntelliTest API",
            "status": "operational",
            "version": "1.0.0",
        }

    return app
