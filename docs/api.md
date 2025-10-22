# MYDY LMS API (Unofficial)

This is the **FastAPI backend** of the MYDY LMS client.  
It provides endpoints for authentication, semesters, courses, documents, and attendance data.

---

## API Access

Once the client is running, the API can be accessed at:

- **API Base URL:** [http://127.0.0.1:8000/api](http://127.0.0.1:8000/api)
- **Swagger UI / API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Endpoints Overview

### System

- `GET /api/` – Root endpoint with basic API info
- `GET /api/health` – Health check

### Authentication

- `POST /api/auth/login` – Login with email and password
- `GET /api/auth/me` – Get logged-in user profile
- `GET /api/auth/creds` – View stored credentials
- `DELETE /api/auth/logout` – Logout current user

### Semesters

- `GET /api/sem/` – List all semesters
- `GET /api/sem/{sem_no}/course` – Courses in a semester

### Courses

- `GET /api/course/{course_id}/docs` – Course contents

### Documents

- `GET /api/doc/{doc_id}` – Document metadata, view, or download

### Attendance

- `GET /api/att/` – Overall attendance
- `GET /api/att/courses` – Attendance for all courses
- `GET /api/att/course/{altid}` – Attendance for a specific course

---

## Notes

- Authentication tokens are stored locally after a successful login.
- Data is cached in `./data/` for faster subsequent access.
- All endpoints return structured JSON with `status`, `data`, and `errors`.
- Documents can be viewed inline or downloaded.

---

## Disclaimer

This API is **unofficial** and intended for **educational and personal use**.  
It is **not affiliated with or endorsed by DY Patil University**.

Use responsibly. The author is **not responsible for misuse, data loss, or violations of institutional policies**.
