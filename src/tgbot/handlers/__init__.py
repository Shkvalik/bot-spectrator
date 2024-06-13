from .admin import router as admin_router
from .user import router as user_router
from .echo import router as echo_router
from .incognito import router as incognito_router
from .paginations import router as pagination_router

routers_list = [
    pagination_router,
    admin_router,
    user_router,
    echo_router,
    incognito_router,
]

__all__ = [
    'routers_list',
]
