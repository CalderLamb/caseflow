from fastapi import APIRouter
from app.api.v1 import queue, items, drafts, matters, review_slots, auth

router = APIRouter()

router.include_router(auth.router, tags=["auth"])
router.include_router(queue.router, tags=["queue"])
router.include_router(items.router, tags=["items"])
router.include_router(drafts.router, tags=["drafts"])
router.include_router(matters.router, tags=["matters"])
router.include_router(review_slots.router, tags=["review-slots"])
