<div align="center">

# MYDY LMS CLIENT (Unofficial)

An unofficial client for **[mydylms](https://mydy.dypatil.edu/)**, including the [API](https://github.com/viraj-sh/mydylms-client/wiki/API-Documentation), [Frontend](https://github.com/viraj-sh/mydylms-client/wiki/Frontend-Documentation), and [MCP Server](https://github.com/viraj-sh/mydylms-client/wiki/MCP-Documentation), developed for educational purposes and not affiliated with DY Patil or MYDY.

<a href="https://github.com/viraj-sh/mydylms-client/releases/latest">
  <img src="https://img.shields.io/github/v/release/viraj-sh/mydylms-client?label=Latest%20Release&color=green&style=flat-square&cacheSeconds=3600" alt="Release"/>
</a>
<a href="https://hub.docker.com/r/virajsh/mydylms-client">
  <img src="https://img.shields.io/docker/v/virajsh/mydylms-client?label=Docker&color=blue&sort=semver&style=flat-square" alt="Docker"/>
</a>
<a href="https://github.com/viraj-sh/mydylms-client/wiki">
  <img src="https://img.shields.io/badge/docs-wiki-orange?style=flat-square" alt="Wiki"/>
</a>

</div>


---
## What Makes This Client Better than Official MYDY LMS

This client improves on the official MyDY LMS by making document access and browsing simpler and more efficient:

* **Easy Access:** View or download any document directly—no FlexPaper or hidden links.
* **Accurate File Names:** Displays the actual file name instead of vague titles.
* **Direct Navigation:** One-click view/download for documents and URLs.
* **Upload Date & Time:** See when each document was uploaded.
* **Search & Filters:** Search by file name, sort by date, filter by mod type.
* **Full Semester Access:** Quickly access documents from all semesters and subjects.
* **Optimized Performance:** Caching ensures faster loading.
* **Open API & MCP Server:** Open-sourced endpoints for custom frontends and integrations.

---

## Overview

This repository includes:

- **[API](https://github.com/viraj-sh/mydylms-client/wiki/API-Documentation):** FastAPI-based backend for authentication, semesters, subjects, documents, and attendance.
- **[Frontend](https://github.com/viraj-sh/mydylms-client/wiki/Frontend-Documentation):** Static interface for interacting with the API.
- **[MCP Server](https://github.com/viraj-sh/mydylms-client/wiki/MCP-Documentation):** Endpoint (`/mcp`) compatible with Model Context Protocol (MCP) clients such as LLM Clients, LangChain bots, etc.

The client can be run using a **[prebuilt release](https://github.com/viraj-sh/mydylms-client/releases/latest)** (recommended), **[built from source](#option-1-building-from-source-without-docker)**, or **[Docker](#option-2-running-with-docker)**. Quick deployment is also supported on **Render**.

<a href="https://render.com/deploy?repo=https://github.com/viraj-sh/mydylms-client" target="_blank">
  <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render" width="180"/>
</a>

---

### Available Services

Once the client is running, the following endpoints are accessible (the host may vary, but the paths remain the same):

- **API:** [http://127.0.0.1:8000/api](http://127.0.0.1:8000/api)

  - **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

- **Frontend:** [http://localhost:8000](http://localhost:8000)
- **MCP Server:** [http://localhost:8000/mcp](http://localhost:8000/mcp)
---

## Option 1: Building from Source (Without Docker)

```bash
git clone https://github.com/viraj-sh/mydylms-client
cd mydylms-client

python -m venv venv

venv\Scripts\activate # Windows
source venv/bin/activate # macOS/Linux

pip install --upgrade pip
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

### 3. Docker Compose

A [`docker-compose.yaml`](https://github.com/viraj-sh/mydylms-client/blob/main/docker-compose.yaml) is included in the repository.

```bash
# using curl
curl -L -o docker-compose.yaml https://github.com/viraj-sh/mydylms-client/raw/main/docker-compose.yaml 

# using wget
wget -O docker-compose.yaml https://github.com/viraj-sh/mydylms-client/raw/main/docker-compose.yaml 

docker-compose up -d
```



---

## Disclaimer

This project is **unofficial** and intended for personal and educational use only.
DY Patil or MyDY is **not associated** with this project.

Use responsibly. The author is **not liable for misuse, data loss, or violations of institutional policies**.
