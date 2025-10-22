# MYDYLMS Frontend (Unofficial)

**Note:** This is an unofficial frontend for the [mydylms-api](api.md).  
It is made purely for educational purposes and is **not affiliated with or endorsed by DY Patil or mydy**. Logos and branding used here are for demonstration only.

---

## Preview

<a href="https://raw.githubusercontent.com/viraj-sh/mydylms-client/main/frontend/src/images/preview_login.png">
  <img src="https://raw.githubusercontent.com/viraj-sh/mydylms-client/main/frontend/src/images/preview_login.png" width="250" alt="Login Page"/>
</a>
<a href="https://raw.githubusercontent.com/viraj-sh/mydylms-client/main/frontend/src/images/preview_dashboard.png">
  <img src="https://raw.githubusercontent.com/viraj-sh/mydylms-client/main/frontend/src/images/preview_dashboard.png" width="250" alt="Dashboard"/>
</a>
<a href="https://raw.githubusercontent.com/viraj-sh/mydylms-client/main/frontend/src/images/preview_attendance.png">
  <img src="https://raw.githubusercontent.com/viraj-sh/mydylms-client/main/frontend/src/images/preview_attendance.png" width="250" alt="Attendance Page"/>
</a>

---

## Overview

This frontend provides a user interface for:

- Logging in via email and password.
- Viewing semesters, subjects, and documents.
- Viewing attendance details for each subject.
- Searching and filtering documents by title and type.
- Logging out.

It is designed to work **exclusively with the [mydylms-api](api.md)**. Nothing will function without the API.

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
- **Search & Filter:** Search documents by title and filter by mod type.

### 3. Attendance Page

- **Overall Attendance:** Displays overall attendance percentage.
- **Detailed Attendance:** Shows attendance per subject.
- **View Individual Attendance:** Clicking **View** displays detailed class-level attendance.

### 4. Logout

- Logs the user out and redirects to the login page.

---

## Technical Details

- Communicates exclusively with the [mydylms-api](api.md).
- Default API URL: `http://127.0.0.1:8000/api`.
- Fully client-side; depends on the API for data.
- JS files are structured according to the API endpoints.

---

## Disclaimer

This frontend is **unofficial** and intended for **personal/educational use**.  
DY Patil or MyDY is **not associated** with this project.
