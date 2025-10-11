# V3.0 API Rewrite

**Status:** ~90% complete

This branch contains a complete rewrite of the Moodle API wrapper for personal use. The API is mostly functional, with all core endpoints implemented. Core modules are used internally and should not be accessed directly.

## System Endpoints

- `GET /`  
  Root endpoint

- `GET /health`  
  Health check

## Auth Endpoints

- `POST /auth/login`  
  Login with email and password

- `GET /auth/token`  
  Validate current token _(flaky in tests, skipped)_

- `GET /auth/me`  
  Get logged-in user profile

- `GET /auth/creds`  
  Get current user credentials

- `DELETE /auth/logout`  
  Logout current user

## Semester Endpoints

- `GET /sem/`  
  Get all semesters

- `GET /sem/{sem_no}/course`  
  Get all courses in a given semester

## Course Endpoints

- `GET /course/{course_id}/docs`  
  Get course contents

## Document Endpoints

- `GET /doc/{doc_id}`  
  Document metadata, view, or download handler

## Attendance Endpoints

- `GET /att/`  
  Get overall attendance

- `GET /att/courses`  
  Get attendance for all courses

- `GET /att/course/{altid}`  
  Get attendance for a given course

## Notes

- The API is fully functional for most endpoints.
- Core modules are used internally; external access is not recommended.
- Some endpoints (like `/auth/token`) may behave inconsistently in automated tests due to runtime `.env` dependencies.
- Intended for personal development and testing.
