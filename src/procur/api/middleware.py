"""Custom middleware for API."""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..db.repositories import AuditRepository
from ..db import get_db_session


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to log API requests to audit trail."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log to audit trail."""
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log to audit trail (async, don't block response)
        try:
            self._log_request(request, response, process_time)
        except Exception:
            # Don't fail request if audit logging fails
            pass
        
        return response
    
    def _log_request(self, request: Request, response: Response, process_time: float):
        """Log request to audit trail."""
        # Skip health checks and static files
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return
        
        try:
            db = get_db_session()
            with db.get_session() as session:
                audit_repo = AuditRepository(session)
                
                # Extract user info from request state if available
                user_id = getattr(request.state, "user_id", None)
                
                # Log the request
                audit_repo.log_action(
                    action=f"{request.method}_{request.url.path}",
                    resource_type="api_request",
                    actor_type="user" if user_id else "anonymous",
                    user_id=user_id,
                    event_data={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "process_time": process_time,
                    },
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )
        except Exception:
            # Silently fail - don't break the request
            pass


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID to response headers."""
        import uuid
        
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response
