from .post_content import router as post_content_router
from .interface import router as interface_router
from .registration import router as reg_router
from .before_reg import router as before_reg_router

from .settings import router as settings_router

from ..utils.filter import RegFilter

for r in [post_content_router, interface_router, settings_router]:
    r.message.filter(RegFilter())
    r.callback_query.filter(RegFilter())

routers = [
    before_reg_router,
    post_content_router,
    settings_router,
    interface_router,
    reg_router
]