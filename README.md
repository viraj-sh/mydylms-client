## MYDY LMS API (Unofficial)

This is a FastAPI-based wrapper for the MYDY LMS.  
It provides endpoints to access login, semesters, subjects, documents, and attendance data.

---

### Installation

```bash
pip install -r requirements.txt
```

---

### Running the Server (Locally)

```bash
uvicorn api:app --reload
```

API will be available at:

- [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Running with Docker

You can run this API using Docker in two ways:

#### 1. Build Locally

A `Dockerfile` is included in the root directory.
To build and run:

```bash
docker build -t mydylms-api .
docker run -p 8000:8000 mydylms-api
```

#### 2. Use Prebuilt Image from Docker Hub

A prebuilt image is available on Docker Hub:

```bash
docker pull virajsh/mydylms-api:latest
docker run -p 8000:8000 virajsh/mydylms-api:latest
```

API will be available at:

- [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Endpoints Overview

#### System

- `GET /` – Root endpoint
  Returns a basic API info message.

- `GET /health` – Health check
  Returns service status and uptime confirmation.

#### Auth Endpoints

- `POST /auth/login` - Login with email and password

- `GET /auth/token` - Validate current token _(flaky in tests, skipped)_

- `GET /auth/me` - Get logged-in user profile

- `GET /auth/creds` - Get current user credentials

- `DELETE /auth/logout` - Logout current user

#### Semester Endpoints

- `GET /sem/` - Get all semesters

- `GET /sem/{sem_no}/course` - Get all courses in a given semester

#### Course Endpoints

- `GET /course/{course_id}/docs` - Get course contents

#### Document Endpoints

- `GET /doc/{doc_id}` - Document metadata, view, or download handler

#### Attendance Endpoints

- `GET /att/` - Get overall attendance

- `GET /att/courses` - Get attendance for all courses

- `GET /att/course/{altid}` - Get attendance for a given course

---

### Notes

- Authentication credentials and tokens are stored locally after a successful `/auth/login`.
- Use `/auth/creds` to view stored credentials (passwords are never returned or saved).
- Documents can be either viewed inline or downloaded, depending on the chosen endpoint.
- Data is cached and stored locally in the `./data/` directory for faster subsequent access.
- All endpoints return structured JSON responses with `status`, `data` and `errors`.
- Some endpoints (like /auth/token) may behave inconsistently in automated tests due to runtime .env dependencies.

---

### Related Project

For a complete setup (API + frontend), check out the combined client:  
[mydylms-client (Unofficial)](https://github.com/viraj-sh/mydylms-client) — includes this API and a web interface with Docker Compose support.

---

### Usage and Disclaimer

- This project is for **personal and educational purposes only**.
- It is **not affiliated with, endorsed by, or supported by DY Patil University**.
- Use of this API is at your own risk. The author is **not responsible for any misuse, data loss, or violations of institutional policies**.
- Do not use this to overload, abuse, or disrupt official LMS services.
