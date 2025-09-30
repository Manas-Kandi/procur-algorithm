"""Health check endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ...db import get_session
from ..config import get_api_config
from ..schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check API and database health",
)
def health_check(session: Session = Depends(get_session)):
    """Health check endpoint."""
    config = get_api_config()
    
    # Check database connectivity
    try:
        session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "timestamp": datetime.utcnow(),
        "version": config.version,
        "database": db_status,
    }


@router.get(
    "/",
    summary="Root endpoint",
    description="API root with basic information",
)
def root():
    """Root endpoint."""
    config = get_api_config()
    return {
        "name": config.title,
        "version": config.version,
        "description": config.description,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }
