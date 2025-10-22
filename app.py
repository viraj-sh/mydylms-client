from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.system import router as system_router
from api.course import router as course_router
from api.attendance import router as attendance_router
from api.document import router as document_router
from api.auth import router as auth_router
from api.semester import router as semester_router
from core.logging_config import setup_logging
from core.exceptions import add_exception_handlers
from fastapi_mcp import FastApiMCP

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

setup_logging()
logger = logging.getLogger("mydylms")

app = FastAPI(title="Unofficial mydylms-client API")

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

add_exception_handlers(app)
logger.info("Application startup complete")

app.mount("/static", StaticFiles(directory="frontend"), name="frontend_static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("frontend/index.html")


# Include routers
app.include_router(system_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(semester_router, prefix="/api")
app.include_router(course_router, prefix="/api")
app.include_router(document_router, prefix="/api")
app.include_router(attendance_router, prefix="/api")

mcp = FastApiMCP(
    app,
    include_operations=[
        "get_system_info",
        "check_system_health",
        "login_user",
        "validate_login_session",
        "get_user_profile",
        "get_user_credentials",
        "logout_user",
        "get_all_semesters",
        "get_semester_courses",
        "get_course_documents",
        "get_document_by_id",
        "get_overall_attendance",
        "get_all_course_attendance",
        "get_course_attendance",
    ],
)
mcp.mount_http()

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
