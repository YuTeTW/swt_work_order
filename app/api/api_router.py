from fastapi import APIRouter
from app.api import authentication, user, item, order, order_message

router = APIRouter()

router.include_router(authentication.router, tags=["authentication"])
router.include_router(user.router, tags=["user"])
# router.include_router(item.router, tags=["item"])
# router.include_router(order.router, tags=["order"])
# router.include_router(order_message.router, tags=["order_message"])
