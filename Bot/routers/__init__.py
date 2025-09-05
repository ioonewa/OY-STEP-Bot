from .post_content import router as post_content_router
from .interface import router as interface_router
from .registration import router as reg_router

from ..utils.filter import RegFilter

for r in [post_content_router, interface_router]:
    r.message.filter(RegFilter())

routers = [
    reg_router,
    post_content_router,
    interface_router
]