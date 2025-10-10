from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.system import router as system_router
from api.course import router as course_router
from api.attendance import router as attendance_router
from api.auth import router as auth_router
from api.semester import router as semester_router
from core.logging_config import setup_logging
from core.exceptions import add_exception_handlers

setup_logging()
logger = logging.getLogger("mydylms")

app = FastAPI(title="Unofficial mydylms-client API")

origins = [
    "http://127.0.0.1:5500",
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

# Include routers
app.include_router(system_router)
app.include_router(auth_router)
app.include_router(semester_router)
app.include_router(course_router)
app.include_router(attendance_router)
