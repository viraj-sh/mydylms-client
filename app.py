import os
import sys
import uvicorn

if __name__ == "__main__":
    app_dir = os.path.join(os.path.dirname(__file__), "app")
    sys.path.insert(0, app_dir)

    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )