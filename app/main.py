"""FastAPI application - Motor de Autorização de Benefícios Flexíveis."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.config import get_settings
from app.database import init_db
from app.api.v1 import router as v1_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialização e shutdown da aplicação."""
    # startup: opcional criar tabelas (em prod use migrations)
    # await init_db()
    yield
    # shutdown
    pass


app = FastAPI(
    title=settings.app_name,
    description="API de autorização baseada em ISO 8583 para cartões de benefícios flexíveis.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(v1_router, prefix="/v1", tags=["v1"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}
