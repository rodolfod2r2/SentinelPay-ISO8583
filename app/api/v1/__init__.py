"""Rotas v1."""
from fastapi import APIRouter
from app.api.v1.authorize import router as authorize_router

router = APIRouter()
router.include_router(authorize_router, prefix="/authorize", tags=["authorize"])
