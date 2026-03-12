GithubTool README
Overview
GithubTool is a desktop GUI application for managing GitHub repositories. It supports cloning/updating repositories, downloading release assets (all releases or latest only), creating and uploading new repositories (personal or organization), and exporting repository lists to CSV or TXT. The app includes startup system checks and robust network handling for slow or flaky connections.

Project Structure
Key files

gui.py — Tkinter GUI and startup system checks.

download_core.py — Clone/update and release download flow; supports latest_only.

repo_create_core.py — Create and upload repository flow (uses gh CLI or REST API fallback).

csv_core.py — Export repositories to CSV/TXT with pagination.

auth_token.py — Centralized token lookup (get_token).

network_utils.py — Shared network helpers (retry_requests, parse_link_header, parse_oauth_scopes_from_headers).

ght.version — Project version file (may be prepopulated or stamped at build time).

GithubTool.spec — PyInstaller spec used by the build script.

GHbuild_exe.bat — Windows build wrapper (optional stamping and provenance).

Requirements
Runtime

Python 3.8+

requests Python package

git installed and on PATH (critical)

Optional: gh (GitHub CLI) for interactive repo creation and push

Permissions

Write permission to the working directory for exports and downloads.

Quick Start (Development)
Create and activate a virtual environment

bash
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # macOS / Linux
Install dependencies

bash
pip install requests pyinstaller
Run the GUI

bash
python gui.py
The app runs a startup system check. If critical requirements are missing, a modal lists issues and disables Create/Export until resolved.

Usage
Clone / Update Repo — clones or pulls a repository to the chosen local folder.

Download Releases — choose All or Latest only via the Releases radio control.

Create & Upload Repo — creates a new repository; private creation requires a token with repo scope.

Export — export repositories to CSV or TXT; check Include private repos to include private repositories (requires token with repo scope).

Logging and Progress — operations report progress and log messages in the GUI.

Build and Packaging (Windows)
Build script: GHbuild_exe.bat (place in GithubTool folder)

Basic build (preserve existing ght.version):

bat
GHbuild_exe.bat 1.0.0
Clean build and stamp ght.version with git provenance:

bat
GHbuild_exe.bat 1.0.0 --clean --stamp
--clean removes previous build/, dist/, and __pycache__.

--stamp overwrites ght.version with version, build_time, git_commit, and git_branch.

Output artifacts are copied to dist\GithubTool_build\<version>\ and include ght.version and the spec file.

POSIX build

Activate venv and run:

bash
pyinstaller --clean --noconfirm GithubTool.spec
To stamp ght.version on POSIX:

bash
echo "version=1.0.0" > ght.version
echo "build_time=$(date)" >> ght.version
echo "git_commit=$(git rev-parse --short HEAD 2>/dev/null || echo unknown)" >> ght.version
echo "git_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)" >> ght.version
Testing Checklist
Startup checks — run python gui.py; confirm no dialog when requirements are met.

Download flows — test All on a repo with many releases and Latest only on a repo with at least one release.

Create & Upload — test personal and org creation; verify token scope enforcement.

Export — export public owner (no token) and authenticated user with private repos (token with repo scope).

Build — run GHbuild_exe.bat 1.0.0 --clean --stamp and verify dist\GithubTool_build\1.0.0 contains the exe and ght.version. Test the built exe on a clean VM.

Notes and Recommendations
Single source of truth: use auth_token.py for token lookup and network_utils.py for network helpers to avoid duplication.

Preserve ght.version: the build script will not overwrite ght.version unless --stamp is used.

Slow networks: downloads use streaming, small chunk sizes, and retries; adjust download_core.py parameters (chunk_size, throttle_delay, timeouts) if needed.

Spec and icon: keep app.ico and version handling in the spec if you prefer embedding resources via PyInstaller rather than in-code embedding.
