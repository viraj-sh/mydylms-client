# MYDY LMS CLIENT (Unofficial)

**Note:** This is an unofficial client for **[mydylms](https://mydy.dypatil.edu/)**, including the [frontend](docs/frontend.md), [api](docs/api.md), and [mcp server](docs/mcp.md).  
It is developed for educational purposes and is **not affiliated with or endorsed by DY Patil or mydy**. Logos and branding are used for demonstration only.

---

## Overview

This repository includes:

- **[API](docs/api.md):** FastAPI-based backend for authentication, semesters, subjects, documents, and attendance.
- **[Frontend](docs/frontend.md):** Static interface for interacting with the API.
- **[MCP Server](docs/mcp.md):** Endpoint (`/mcp`) compatible with Model Context Protocol (MCP) clients such as LLM Clients, LangChain bots, etc.

The client can be run using **[built from source](#option-1-building-from-source-without-docker)** or **[Docker](#option-2-running-with-docker)**.  
Quick deployment is also supported on **Render**.

<a href="https://render.com/deploy?repo=https://github.com/viraj-sh/mydylms-client" target="_blank">
  <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render" width="180"/>
</a>

---

## Option 1: Building from Source (Without Docker)

```bash
git clone https://github.com/viraj-sh/mydylms-client
cd mydylms-client
pip install -r requirements.txt
python app.py
```

---

## Option 2: Running with Docker

### 1. Use Prebuilt Image from Docker Hub (Recommended)

```bash
docker pull virajsh/mydylms-client:latest
docker run -p 8000:8000 virajsh/mydylms-client:latest
```

### 2. Build Locally

A `Dockerfile` is included in the repository.

```bash
git clone https://github.com/viraj-sh/mydylms-client
cd mydylms-client
docker build -t mydylms-client .
docker run -p 8000:8000 mydylms-client
```

---

### After Running (for Both Methods)

Once the client is running, the following services will be available:

- **API:** [http://127.0.0.1:8000/api](http://127.0.0.1:8000/api)

  - **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

- **Frontend:** [http://localhost:8000](http://localhost:8000)
- **MCP Server:** [http://localhost:8000/mcp](http://localhost:8000/mcp)

---

## Disclaimer

This project is **unofficial** and intended for personal and educational use only.
DY Patil or MyDY is **not associated** with this project.

Use responsibly. The author is **not liable for misuse, data loss, or violations of institutional policies**.
