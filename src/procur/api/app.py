"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from ..db import init_db
from .config import get_api_config
from .routes import (
    auth_router,
    contracts_router,
    health_router,
    negotiations_router,
    requests_router,
    vendors_router,
)


def get_limiter() -> Limiter:
    """Create rate limiter instance."""
    return Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    config = get_api_config()
    print(f"Starting {config.title} v{config.version}")
    
    # Initialize database
    try:
        init_db(create_tables=False)  # Tables should be created via migrations
        print("Database connection established")
    except Exception as e:
        print(f"Warning: Database connection failed: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down API")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    config = get_api_config()
    
    # Create FastAPI app
    app = FastAPI(
        title=config.title,
        description=config.description,
        version=config.version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=config.cors_allow_credentials,
        allow_methods=config.cors_allow_methods,
        allow_headers=config.cors_allow_headers,
    )
    
    # Configure rate limiting
    if config.rate_limit_enabled:
        limiter = get_limiter()
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Register routers
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(requests_router)
    app.include_router(vendors_router)
    app.include_router(negotiations_router)
    app.include_router(contracts_router)
    
    # Custom exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": exc.errors(),
                "error_code": "validation_error",
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error_code": "internal_error",
            },
        )
    
    return app


# Create app instance
app = create_app()
