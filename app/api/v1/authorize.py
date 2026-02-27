"""Endpoint POST /v1/authorize."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.authorize import AuthorizeRequest, AuthorizeResponse
from app.services.authorization_service import AuthorizationService

router = APIRouter()


@router.post("", response_model=AuthorizeResponse)
async def authorize(
    request: AuthorizeRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthorizeResponse:
    """
    Autorização de transação baseada em ISO 8583.
    metadata: tenant_id e operadora (Visa | Mastercard | Elo).
    iso_8583: MTI, DE2 (PAN), DE4 (valor), DE18 (MCC), DE42, DE48, DE49.
    """
    svc = AuthorizationService(db)
    return await svc.authorize(request)
