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
python app.py
```

API will be available at:

- [http://127.0.0.1:8000/api](http://127.0.0.1:8000/api)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Running with Docker

You can run this API using Docker in two ways:

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

API will be available at:

- [http://127.0.0.1:8000/api](http://127.0.0.1:8000/api)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Endpoints Overview

#### System

- `GET /api/` – Root endpoint
  Returns a basic API info message.

- `GET /api/health` – Health check
  Returns service status and uptime confirmation.

#### Auth Endpoints

- `POST /api/auth/login` - Login with email and password

- `GET /api/auth/token` - Validate current token _(flaky in tests, skipped)_

- `GET /api/auth/me` - Get logged-in user profile

- `GET /api/auth/creds` - Get current user credentials

- `DELETE /api/auth/logout` - Logout current user

#### Semester Endpoints

- `GET /api/sem/` - Get all semesters

- `GET /api/sem/{sem_no}/course` - Get all courses in a given semester

#### Course Endpoints

- `GET /api/course/{course_id}/docs` - Get course contents

#### Document Endpoints

- `GET /api/doc/{doc_id}` - Document metadata, view, or download handler

#### Attendance Endpoints

- `GET /api/att/` - Get overall attendance

- `GET /api/att/courses` - Get attendance for all courses

- `GET /api/att/course/{altid}` - Get attendance for a given course

---

### Notes

- Authentication credentials and tokens are stored locally after a successful `/api/auth/login`.
- Use `/api/auth/creds` to view stored credentials (passwords are never returned or saved).
- Documents can be either viewed inline or downloaded, depending on the chosen endpoint.
- Data is cached and stored locally in the `./data/` directory for faster subsequent access.
- All endpoints return structured JSON responses with `status`, `data` and `errors`.
- Some endpoints (like `/api/auth/token`) may behave inconsistently in automated tests due to runtime .env dependencies.

---

### Usage and Disclaimer

- This project is for **personal and educational purposes only**.
- It is **not affiliated with, endorsed by, or supported by DY Patil University**.
- Use of this API is at your own risk. The author is **not responsible for any misuse, data loss, or violations of institutional policies**.
- Do not use this to overload, abuse, or disrupt official LMS services.
