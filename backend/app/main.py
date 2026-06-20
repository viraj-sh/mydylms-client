from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx

from app.routes import system, auth, user
from app.core.config import settings
from app.core.http import http_state


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    http_state.client = httpx.AsyncClient()
    yield
    # Shutdown
    await http_state.client.aclose()


app = FastAPI(
    title=settings.project_name,
    description=settings.project_name,
    version=settings.version,
    lifespan=lifespan,
)

app.include_router(router=system.router, prefix="", tags=["system"])
app.include_router(router=auth.router, prefix="/auth", tags=["auth"])
app.include_router(router=user.router, prefix="/user", tags=["user"])
