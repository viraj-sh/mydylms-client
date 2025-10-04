# MYDY LMS CLIENT (Unofficial)

**Note:** This is an unofficial combined client for **mydylms**, including both the [mydylms-frontend](https://github.com/Viraj-S45/mydylms-frontend) and [mydylms-api](https://github.com/viraj-sh/mydylms-api).
It is made purely for educational purposes and is **not affiliated with or endorsed by DY Patil or mydy**. Logos and branding used here are for demonstration only.

---

## Overview

This repository combines:

- **[mydylms-api](https://github.com/viraj-sh/mydylms-api):** A FastAPI-based backend for authentication, semesters, subjects, documents, and attendance.
- **[mydylms-frontend](https://github.com/Viraj-S45/mydylms-frontend):** A static frontend interface to access the API data.

You can run the client **either with Docker** (recommended) or **manually** by running the frontend and API separately.

---

Got it! Here’s the updated **Docker Compose usage section** where users only need the [`docker-compose.yaml`](https://raw.githubusercontent.com/viraj-sh/mydylms-client/main/docker-compose.yaml) file:

---

## Option 1: Using Docker Compose (Recommended)

You can start both API and frontend with **one command** using the `docker-compose.yaml` file directly.

### Steps:

1. Create a directory for the client and navigate into it:

```bash
mkdir -p mydylms-client && cd mydylms-client
```

2. Download the `docker-compose.yaml` file:

```bash
curl -O https://raw.githubusercontent.com/viraj-sh/mydylms-client/main/docker-compose.yaml
```

3. Run Docker Compose:

```bash
docker compose up -d
```

4. Access the services:

- Frontend: [http://localhost:3000](http://localhost:3000)
- API: [http://localhost:8000](http://localhost:8000)

5. To stop:

```bash
docker compose down
```

**Notes:**

- The frontend container will automatically connect to the API container.
- You can change host ports in `docker-compose.yml` if needed.

---

## Option 2: Manual Run (Without Docker)

You can run the frontend and API separately without Docker.

### 1. Run the API

```bash
cd mydylms-api
pip install -r requirements.txt
uvicorn api:app --reload
```

- API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 2. Run the Frontend

```bash
cd mydylms-frontend
# Using Python's simple HTTP server
python3 -m http.server 3000
```

- Frontend will be available at [http://localhost:3000](http://localhost:3000)
- Make sure to update the **API URL** in the frontend JS if the API is running on a different host or port.

---

## Technical Details

- Frontend communicates exclusively with the API.
- Default API URL in frontend: `http://127.0.0.1:8000`
- Fully client-side frontend; backend must be running for functionality.
- API stores cached data in `./data/` for faster subsequent access.

---

## Future Plans

- Additional features as the API evolves.

---

## Disclaimer

This project is **unofficial** and made for personal/educational use. DY Patil or MyDY is **not associated** with this project.

Use responsibly. The author is **not responsible for misuse, data loss, or violations of institutional policies**.
