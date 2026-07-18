import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi_mcp import FastApiMCP

from app.core.config import settings
from app.core.http import NullCookieJar, http_state
from app.core.utils import static_path
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

static_dir = static_path()

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

mcp = FastApiMCP(
    app,
    name="MYDY LMS MCP (Unofficial)",
    description="MCP server for MYDY LMS",
    include_operations=[
        "get_user_profile_detailed",
        "get_user_profile",
        "get_current_semester_courses",
        "get_enrolled_courses",
        "get_course_docs",
        "get_calendar_events",
        "get_all_announcements",
        "fetch_latest_annoucements",
        "get_attendance",
    ],
    headers=["authorization", "x-user-id", "x-api-key"],
)
mcp.mount_http()

print(
    f"static_dir -> {static_dir} | exists? -> {os.path.isdir(static_dir)} | index.html exists? -> {os.path.isfile(os.path.join(static_dir, 'index.html'))}"
)

if os.path.isdir(static_dir) and os.path.isfile(os.path.join(static_dir, "index.html")):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        return FileResponse(os.path.join(static_dir, "index.html"))
