from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.v1.system import router as system_router
from api.v1.auth import router as auth_router
from api.v1.semester import router as semester_router
from api.v1.course import router as course_router
from api.v1.docs import router as docs_router
from api.v1.attendance import router as attendance_router
from core.logging import setup_logging
from core.utils import frontend_path
from fastapi_mcp import FastApiMCP
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

logger = setup_logging(name="app", level="INFO")

app = FastAPI(title="Unofficial mydylms API v1")

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = frontend_path()

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse(os.path.join(static_dir, "index.html"))

logger.info("Application startup complete")

# Include routers
app.include_router(system_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(semester_router, prefix="/api/v1")
app.include_router(course_router, prefix="/api/v1")
app.include_router(docs_router, prefix="/api/v1")
app.include_router(attendance_router, prefix="/api/v1")

mcp = FastApiMCP(
    app,
    include_operations=[
        "get_system_info",
        "check_system_health",
        "login_user",
        "validateMoodleSession",
        "logoutUser",
        "get_semesters_list",
        "get_courses_in_semester",
        "getUserProfile",
        "get_course_contents_endpoint",
        "getCourseDocument",
        "getAttendanceData",
    ],
)
mcp.mount_http()

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
