from fastapi import APIRouter
from app.api import authentication, user, order, order_message, order_issue

router = APIRouter()

router.include_router(authentication.router, tags=["authentication"])
router.include_router(user.router, tags=["users"])
router.include_router(order.router, tags=["orders"])
router.include_router(order_message.router, tags=["order_messages"])
router.include_router(order_issue.router, tags=["order_issue"])




