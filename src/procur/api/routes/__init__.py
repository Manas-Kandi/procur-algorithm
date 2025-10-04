"""API route modules."""

from .auth import router as auth_router
from .requests import router as requests_router
from .vendors import router as vendors_router
from .negotiations import router as negotiations_router
from .contracts import router as contracts_router
from .health import router as health_router
from .dashboard import router as dashboard_router
from .sourcing import router as sourcing_router
from .demo import router as demo_router
from .portfolio import router as portfolio_router

__all__ = [
    "auth_router",
    "requests_router",
    "vendors_router",
    "negotiations_router",
    "contracts_router",
    "health_router",
    "dashboard_router",
    "sourcing_router",
    "demo_router",
    "portfolio_router",
]
