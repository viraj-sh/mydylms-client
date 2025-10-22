# MYDY LMS CLIENT (Unofficial)

**Note:** This is an unofficial client for **mydylms**, including both the [mydylms-frontend](/frontend/readme.md) and [mydylms-api](/api/README.md).
It is made purely for educational purposes and is **not affiliated with or endorsed by DY Patil or mydy**. Logos and branding used here are for demonstration only.

---

## Overview

This repository combines:

- **[mydylms-api](/api/README.md):** A FastAPI-based backend for authentication, semesters, subjects, documents, and attendance.
- **[mydylms-frontend](/frontend/readme.md):** A static frontend interface to access the API data.

You can run the client **either with Docker** (recommended) or **manually** by running the client.

---

## Option 1: Running with Docker (Recommended)

You can run this **[mydylms-client](https://github.com/viraj-sh/mydylms-client)** using Docker in two ways:

#### 1. Build Locally

A `Dockerfile` is included in the root directory.
To build and run:

```bash
docker build -t mydylms-client .
docker run -p 8000:8000 mydylms-client
```

#### 2. Use Prebuilt Image from Docker Hub

A prebuilt image is available on Docker Hub:

```bash
docker pull virajsh/mydylms-client:latest
docker run -p 8000:8000 virajsh/mydylms-client:latest
```

- API will be available at: [http://127.0.0.1:8000/api](http://127.0.0.1:8000/api)

  - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

- Frontend will be accessible at [http://localhost:8000](http://localhost:8000).
- You can map any host port you like by changing `-p <host_port>:80`.

---

## Option 2: Manual Run (Without Docker)

You can run the CLIENT without Docker.

```bash
git clone https://github.com/viraj-sh/mydylms-client mydylms-client
cd mydylms-client
pip install -r requirements.txt
python app.py
```

- API will be available at: [http://127.0.0.1:8000/api](http://127.0.0.1:8000/api)

  - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

- Frontend will be accessible at [http://localhost:8000](http://localhost:8000).
- You can map any host port you like by changing `-p <host_port>:80`.

---

## Disclaimer

This project is **unofficial** and made for personal/educational use. DY Patil or MyDY is **not associated** with this project.

Use responsibly. The author is **not responsible for misuse, data loss, or violations of institutional policies**.
