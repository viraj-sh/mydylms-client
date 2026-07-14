from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.core.config import settings
from app.core.http import NullCookieJar, http_state
from app.routes import annoucement, attendance, auth, calendar, content, system, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    http_state.client = httpx.AsyncClient()
    yield
    # Shutdown
    await http_state.client.aclose()


app = FastAPI(
    cookies=NullCookieJar(),
    title=settings.project_name,
    description=settings.project_name,
    version=settings.version,
    lifespan=lifespan,
)

app.include_router(router=system.router, prefix="", tags=["system"])
app.include_router(router=auth.router, prefix="/auth", tags=["auth"])
app.include_router(router=user.router, prefix="/user", tags=["user"])
app.include_router(router=attendance.router, prefix="/attendance", tags=["attendance"])
app.include_router(router=content.router, prefix="/content", tags=["content"])
app.include_router(
    router=annoucement.router, prefix="/annoucement", tags=["annoucement"]
)
app.include_router(router=calendar.router, prefix="/calendar", tags=["calendar"])
