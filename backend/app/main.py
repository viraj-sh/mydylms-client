from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.http import NullCookieJar, http_state
from app.routes import annoucement, attendance, auth, calendar, content, system, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    http_state.client = httpx.AsyncClient(
        cookies=NullCookieJar(),
    )
    yield
    # Shutdown
    await http_state.client.aclose()


app = FastAPI(
    title=settings.project_name,
    description=settings.project_name,
    version=settings.version,
    lifespan=lifespan,
)

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=system.router, prefix="", tags=["system"])
app.include_router(router=auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(router=user.router, prefix="", tags=["user"])
app.include_router(
    router=attendance.router, prefix="/v1/attendance", tags=["attendance"]
)
app.include_router(router=content.router, prefix="/v1/content", tags=["content"])
app.include_router(
    router=annoucement.router, prefix="/v1/annoucement", tags=["annoucement"]
)
app.include_router(router=calendar.router, prefix="/v1/calendar", tags=["calendar"])
