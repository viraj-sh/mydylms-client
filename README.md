# V3.0 API Rewrite

**Status:** Early development (~25% complete)

This branch contains a complete rewrite of the Moodle API wrapper for personal use. The current version is in early stages and primarily focused on laying the foundation with core functionality.

## Modules

- **core/auth.py**

  - `get_security_keys`
  - `validate_token`
  - `moodle_login`
  - `get_user_id`
  - `get_sesskey`
  - `logout`

- **core/info.py**

  - `user_profile`
  - `get_semesters`

- **core/course.py**

  - `get_course_contents`

- **core/utils.py**
  - `loadjson`
  - `dumpjson`
  - `fetchhtml`
  - `retrysession`

## Current Focus

- Establishing a clean and modular structure.
- Implementing authentication and course content retrieval.
- Parsing user profile and semester details.

## Notes

- This is a work in progress; most endpoints are partially implemented.
- The code is intended for personal development and testing.
- Expect significant changes in future commits.
