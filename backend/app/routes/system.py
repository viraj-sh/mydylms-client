from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import time

from app.core.config import settings

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def read_root():
    start_time = time.perf_counter()
    print(f"Time: {(time.perf_counter() - start_time):.3f}ms")
    return JSONResponse(
        {
            "name": settings.project_name,
            "version": settings.version,
            "docs_url": "https://github.com/viraj-sh/mydylms-client",
        }
    )


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    start_time = time.perf_counter()
    print(f"Time: {(time.perf_counter() - start_time) * 1000:.3f}ms")
    return JSONResponse({"status": "healthy"})
