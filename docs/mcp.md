# MYDY LMS MCP Server (Unofficial)

The **MCP server** included in the MYDY LMS client provides a **Model Context Protocol (MCP)** interface to interact with the API programmatically.  
It exposes all backend operations as callable tools that can be integrated into MCP-compatible clients, such as VS Code extensions or other automation tools.

---

## MCP Server Access

Once the client is running, the MCP server is available at:

- **MCP Endpoint:** [http://localhost:8000/mcp](http://localhost:8000/mcp)

---

## Configuring MCP Clients

To connect to the MCP server from a client (e.g., VS Code), configure your MCP client with the following:

```json
{
  "servers": {
    "mydylms-client": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

After saving, restart or reload the client. You can now invoke all available MCP tools.

For more details on configuring MCP clients, refer to the [Official FastAPI-MCP Documentation](https://fastapi-mcp.tadata.com/getting-started/quickstart#connecting-a-client-to-the-mcp-server)

---

## Available Tools

The MCP server exposes the following operations:

| Tool                        | Description                                                 |
| --------------------------- | ----------------------------------------------------------- |
| `get_system_info`           | Returns general system information about the server.        |
| `check_system_health`       | Returns server health and uptime status.                    |
| `login_user`                | Authenticate a user with email and password.                |
| `validate_login_session`    | Validates the current login session/token.                  |
| `get_user_profile`          | Fetch the logged-in user's profile.                         |
| `get_user_credentials`      | Fetch the stored user credentials (passwords not returned). |
| `logout_user`               | Logout the current user session.                            |
| `get_all_semesters`         | Retrieve a list of all semesters.                           |
| `get_semester_courses`      | Retrieve all courses for a specific semester.               |
| `get_course_documents`      | List all documents for a specific course.                   |
| `get_document_by_id`        | Retrieve metadata, view, or download a document by ID.      |
| `get_overall_attendance`    | Get overall attendance for the user.                        |
| `get_all_course_attendance` | Get attendance for all courses.                             |
| `get_course_attendance`     | Get attendance for a specific course.                       |

---

## Example Prompts for MCP

Once connected to the MCP server, users can interact with the LMS through natural language prompts or tool calls. Examples:

- **Authentication & Profile**

  - "Log in as mydylms user `user@example.com` with password `password123`."
  - "Who am I logged in as?"
  - "Show my current credentials."

- **Semester & Course Information**

  - "List all semesters available."
  - "Show all courses for semester 3."
  - "What courses do I have this semester?"

- **Course Documents**

  - "List all documents for course `COURSE123`."
  - "Show details for document `DOC456`."
  - "Download the document `DOC789`."

- **Attendance**

  - "Show my overall attendance."
  - "Show attendance for all my courses."
  - "Get attendance for course `COURSE123`."

- **System & Health**

  - "Give me the current system info."
  - "Check the server health and uptime."

---

## Disclaimer

This MCP server is **unofficial** and intended for **educational and personal use**.
It is **not affiliated with or endorsed by DY Patil University**.

Use responsibly. The author is **not responsible for misuse, data loss, or violations of institutional policies**.
