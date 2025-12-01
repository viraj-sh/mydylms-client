<div align="center">

# MYDY LMS CLIENT (Unofficial)

An unofficial client for **[mydylms](https://mydy.dypatil.edu/)**, including the [Frontend](https://github.com/viraj-sh/mydylms-client/wiki/Frontend-Documentation), [MCP Server](https://github.com/viraj-sh/mydylms-client/wiki/MCP-Documentation), and [API](https://github.com/viraj-sh/mydylms-client/wiki/API-Documentation), with support for direct document downloads and full access across all semesters, developed for educational purposes and not affiliated with DY Patil or MYDY.

<a href="https://github.com/viraj-sh/mydylms-client/releases/latest">
  <img src="https://img.shields.io/github/v/release/viraj-sh/mydylms-client?label=Latest%20Release&color=green&style=flat-square&cacheSeconds=3600" alt="Release"/>
</a>
<a href="https://hub.docker.com/r/virajsh/mydylms-client">
  <img src="https://img.shields.io/docker/v/virajsh/mydylms-client?label=Docker&color=blue&sort=semver&style=flat-square" alt="Docker"/>
</a>
<a href="https://github.com/viraj-sh/mydylms-client/wiki">
  <img src="https://img.shields.io/badge/docs-wiki-orange?style=flat-square" alt="Wiki"/>
</a>

</div>


---
## What Makes This Client Better than Official MYDY LMS

This client improves on the official MYDY LMS by making document access and browsing simpler and more efficient:

* **Full Semester Access:** Quickly access documents from all semesters and subjects.
* **Easy Access:** View or download any document directly—no FlexPaper or hidden links.
* **Direct Navigation:** One-click view/download for documents and URLs.
* **Accurate File Names:** Displays the actual file name instead of vague titles.
* **Upload Date & Time:** See when each document was uploaded.
* **Search & Filters:** Search by file name, sort by date, filter by mod type.
* **MCP Server Support:** Enables integration with LLMs for automation or analysis.

---

## Installation & Usage

The client can be run in several ways. For detailed steps, see the **[Getting Started](https://github.com/viraj-sh/mydylms-client/wiki/Getting-Started)** wiki page.

Option 1. **[Prebuilt Releases](https://github.com/viraj-sh/mydylms-client/wiki/Getting-Started#prebuilt-releases)** – Download and run the latest release for your platform:

   [![Windows (.exe)](https://img.shields.io/badge/Windows_\(.exe\)-x64-blue?style=flat-square)](https://github.com/viraj-sh/mydylms-client/releases/latest/mydylms-client.exe)
   [![Linux (.tar.gz)](https://img.shields.io/badge/Linux-x86__64-orange?style=flat-square)](https://github.com/viraj-sh/mydylms-client/releases/latest/download/mydylms-client-linux)
   [![macOS (.zip)](https://img.shields.io/badge/macOS-arm64-lightgrey?style=flat-square)](https://github.com/viraj-sh/mydylms-client/releases/latest/download/mydylms-client-macos)

Option 2. **[One-Click Deployment](https://github.com/viraj-sh/mydylms-client/wiki/Getting-Started#one-click-deployment-render) (Render)** – Deploy the client instantly in the cloud:

   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/viraj-sh/mydylms-client)

Option 3. **[Run from Source](https://github.com/viraj-sh/mydylms-client/wiki/Getting-Started#running-from-source)** – Clone the repository and run the client directly in development mode.

  - For developers who want to modify the client.


    ```bash
    git clone https://github.com/viraj-sh/mydylms-client
    cd mydylms-client

    python -m venv venv
    venv\Scripts\activate   # Windows
    source venv/bin/activate   # macOS/Linux

    pip install --upgrade pip
    pip install -r requirements/base.txt

    python app.py
    ```

Option 4. **[Build from Source](https://github.com/viraj-sh/mydylms-client/wiki/Getting-Started#building-from-source)** – For developers or contributors: clone the repo, install dependencies, and run locally.

Option 5. **[Docker](https://github.com/viraj-sh/mydylms-client/wiki/Getting-Started#docker-deployment)** – Run the client in a consistent containerized environment.

> For complete instructions, platform-specific steps, and Docker usage, see the **[Getting Started wiki](https://github.com/viraj-sh/mydylms-client/wiki/Getting-Started)**.

---
### Available Services

Once the client is running, these endpoints are accessible (host may vary):

* **[Frontend](https://github.com/viraj-sh/mydylms-client/wiki/Frontend-Documentation)** [[http://localhost:8000/](http://localhost:8000/)] : Static interface to interact with the API.
* **[MCP Server](https://github.com/viraj-sh/mydylms-client/wiki/MCP-Documentation)** [[http://localhost:8000/mcp](http://localhost:8000/mcp)] : Endpoint (`/mcp`) compatible with Model Context Protocol (MCP) clients like LLM Clients or LangChain bots.
* **[API](https://github.com/viraj-sh/mydylms-client/wiki/API-Documentation)** [[http://localhost:8000/api](http://127.0.0.1:8000/api)] : FastAPI backend for authentication, semesters, subjects, documents, and attendance.

  * **Interactive Docs:** [[http://localhost:8000/docs](http://127.0.0.1:8000/docs)] : API testing Swagger UI for developers.

---

## MCP Usage

> For full instructions on configuring the MCP server, check out the **[MCP Documentation](https://github.com/viraj-sh/mydylms-client/wiki/MCP-Documentation)**.

| Demo |
| :------------: |
| <img src="https://raw.githubusercontent.com/viraj-sh/mydylms-client/refs/heads/main/.github/assets/mcp_usage.gif" width="800"/> |

## Preview

| Dashboard                                      | Login                                           |
| :-------------------------------------------- | :-------------------------------------------- |
| <img src="https://raw.githubusercontent.com/viraj-sh/mydylms-client/refs/heads/main/.github/assets/preview_dashboard.png" width="500" height="300"/> | <img src="https://raw.githubusercontent.com/viraj-sh/mydylms-client/refs/heads/main/.github/assets/preview_login.png" width="500" height="300"/> |

| Attendance                                    | Profile                                         |
| :------------------------------------------- | :-------------------------------------------- |
| <img src="https://raw.githubusercontent.com/viraj-sh/mydylms-client/refs/heads/main/.github/assets/preview_attendance.png" width="500" height="300"/> | <img src="https://raw.githubusercontent.com/viraj-sh/mydylms-client/refs/heads/main/.github/assets/preview_profile.png" width="500" height="300"/> |



---

## Disclaimer

This project is **unofficial** and intended for personal and educational use only.
DY Patil or MYDY is **not associated** with this project.

Use responsibly. The author is **not liable for misuse, data loss, or violations of institutional policies**.
