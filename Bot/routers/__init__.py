from .post_content import router as post_content_router
from .interface import router as interface_router
from .registration import router as reg_router

routers = [
    reg_router,
    post_content_router,
    interface_router
]