# MyDYLMS Frontend (Unofficial)

**Note:** This is an unofficial frontend for the [mydylms-api](https://github.com/viraj-sh/mydylms-api). It is made purely for educational purposes and is not affiliated with or endorsed by DY Patil or mydy. Logos and branding used here are for demonstration only.

---

## Preview

<a href="/src/images/preview_login.png">
  <img src="/src/images/preview_login.png" width="250" alt="Page 1"/>
</a>
<a href="/src/images/preview_dashboard.png">
  <img src="/src/images/preview_dashboard.png" width="250" alt="Page 2"/>
</a>
<a href="/src/images/preview_attendance.png">
  <img src="/src/images/preview_attendance.png" width="250" alt="Page 3"/>
</a>


---

## Overview

This frontend provides a user interface for:

- Logging in via email and password.
- Viewing semesters, subjects, and documents.
- Viewing attendance details for each subject.
- Searching and filtering documents by title and type.
- Logging out.

It is designed to work **exclusively with the [mydylms-api](https://github.com/viraj-sh/mydylms-api)**. Nothing will function without the API.

---

## Pages

### 1. Login Page

- Users log in with their email and password.
- Successful login redirects to the **Dashboard**.

### 2. Dashboard

- **Semester Selection:** Choose a semester from the top bar.
- **Subjects Sidebar:** Displays subjects for the selected semester.
- **Documents Grid:** Shows documents as cards with:
  - Document title
  - Mod type / document type
  - Document ID
  - **View** and **Download** buttons
    - Documents with `mod_type: url` only have a **View** button.
- **Search & Filter:**
  - Search documents by title.
  - Filter documents by mod type (default: All).

### 3. Attendance Page

- **Overall Attendance:** Displays your overall attendance percentage.
- **Detailed Attendance:** Shows attendance per subject.
- **View Individual Attendance:** Clicking **View** displays detailed class-level attendance for that subject.

### 4. Logout

- Logs the user out and redirects to the login page.

---

## Technical Details

- Frontend communicates exclusively with the [mydylms-api](https://github.com/viraj-sh/mydylms-api).
- Default API URL: `http://127.0.0.1:8000`
  - If the API is hosted elsewhere, update the base URL in all JS files.
- Fully client-side and depends on the local API for data.
- JS files are prefixed according to the API endpoints.

---

## Future Plans

- Integration with a combined repository: `mydylms-alternative-frontend` (frontend + API in one repo).
- Additional features as the API evolves.

---



## Disclaimer

This project is unofficial and made for personal/educational use. DY Patil or MyDY is not associated with this project.
