from .agent_routes import router as agent_router
from .ai_config_routes import router as ai_config_router
from .health_routes import router as health_router
from .repository_routes import router as repository_router
from .user_routes import router as user_router

__all__ = [
    "health_router",
    "user_router",
    "ai_config_router",
    "repository_router",
    "agent_router",
]
