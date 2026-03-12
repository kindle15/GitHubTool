# 🚀 GithubTool v2.0.2

**A comprehensive desktop application for managing GitHub repositories with a
console-first, safety-first design.**

[![Version](https://img.shields.io/badge/version-2.0.2-blue.svg)](https://github.com/kindle15/githubtool)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-proprietary-red.svg)](LICENSE)

---

## 📑 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Token Setup](#-token-setup)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Build and Packaging](#-build-and-packaging)
- [Testing Checklist](#-testing-checklist)
- [FAQ](#-faq)
- [License](#-license)

---

## ✨ Features

### 🆕 What's New in v2.0.2 — Smart Actions Update
- **Tabbed Action Panel** — ⭐ Actions / 🔧 Manage / ⚠️ Danger tabs in the right panel
- **🔑 Token Button** — Check token status or open GitHub token creation page
- **📊 Stats Button** — Dump tab statistics to the diagnostics console (no popup spam)
- **Toggle Privacy** — Switch any repo between Public ↔ Private
- **Fork Repo** — Fork any repository to your account
- **Rename Repo** — Rename a repository directly from the GUI
- **Console-First Design** — Results appear in the diagnostics console, not dialogs

### v2.0.1 Features
- **Push to Branch** — Push an existing local folder to a branch of an existing GitHub repo
- **🚀 Publish Existing Folder** — Publish any local folder to GitHub in one click
- **Download ZIP Fix** — Corrected ZIP download for external repos
- **Delete Repository** — Delete a GitHub repo (with safety confirmation)

### 🛡️ Safety First (v2.0.0+)
- **Pre-Publish Checks** — Verifies repo doesn't exist before creating on GitHub
- **Rollback on Failure** — Deletes the GitHub repo if a push fails after creation
- **Safe Options** — Cancel, Add Remote Only, or View on GitHub first
- **No Data Loss** — Prevents accidental overwrites of existing repositories

### ⚡ Creation Lab (Tab 5)
- **Local Repository Creation** — Create repos with professional structure locally
- **README Templates** — Basic, Detailed, and Minimal formats
- **LICENSE Templates** — MIT, GPL-3.0, Apache-2.0, BSD-3-Clause
- **Git Integration** — Automatic initialization and initial commit
- **GitHub Publishing** — Push directly to GitHub with one click

### 📊 Repository Management
- **My Repos Tab** — View and manage your repositories
- **Organization Repos** — Access team repositories
- **Starred Repos** — Quick access to favorites
- **Smart Public Browsing** — View any user's public repos without authentication

### ⭐ Star Management
- **Star/Unstar** — Manage favorites directly from the GUI
- **Auto-Detect Status** — Shows current star state on selection

### 📤 Export Tools
- **CSV Export** — Structured data format for spreadsheets
- **TXT Export** — Formatted, readable text with aligned columns

### 📥 Download Tools
- **Download Repos** — Get source code as ZIP
- **Clone Repos** — One-click `git clone` (depth=1)
- **Release Assets** — Download binaries and attachments
- **README Viewer** — Preview README files before downloading

---

## 📸 Screenshots

### Main Interface (v2.0.2 — Tabbed Right Panel)

```
┌────────────────────────────────────────────────────────────────────────┐
│ File  Settings  Help                                                   │
├────────────────────────────────────────────────────────────────────────┤
│ Git: ✓ | Auth: ✓ | Token: ghp_***abc | Network: ✓ | Mode: Tools       │
├────────────────────────────────────────────────────────────────────────┤
│ [Refresh] [🔑 Token] [📊 Stats] | Export: ○CSV ●TXT [Export] | [Search]│
├───────────────────────────────┬────────────────────────────────────────┤
│ Welcome | My Repos | Org      │ GitHub API Rate Limit                  │
│ Repos | Starred | Download    │ 4,850 / 5,000 remaining                │
│ From Others | Creation Lab    │ ████████████████░░ 97%                 │
│                               │ [Refresh Rate Limit]                   │
│ ┌───────────────────────────┐ ├────────────────────────────────────────┤
│ │ Name  | Private | Fork   │ │ Repository Details                     │
│ │ repo1 | No      | No     │ │ Name: my-awesome-project               │
│ │ repo2 | Yes     | No     │ │ Private: No  Stars: ⭐ 42              │
│ │ repo3 | No      | Yes    │ ├──────────┬──────────┬──────────────────┤
│ └───────────────────────────┘ │ ⭐ Actions│ 🔧 Manage│ ⚠️ Danger        │
│                               ├──────────┴──────────┴──────────────────┤
│                               │ [🌐 Open]  [📥 Clone]                  │
│                               │ [📦 ZIP]   [⭐ Star]                   │
├───────────────────────────────┴────────────────────────────────────────┤
│ Diagnostics Console (drag divider above to resize ↕)                  │
│ 2026-03-10 10:23:45 - Fetched 42 repositories                         │
└────────────────────────────────────────────────────────────────────────┘
```

### Creation Lab (Tab 5)

```
┌────────────────────────────────────────────────────────────────────────┐
│ ⚡ Creation Lab                                                         │
├────────────────────────────────────────────────────────────────────────┤
│ Step 1: Repository Details                                             │
│   Repository Name: [my-awesome-project_______________________]         │
│   Description:     [A cool new tool__________________________]         │
│   Parent Folder:   [C:\Users\me\projects]  [Browse...]                │
├───────────────────────────────┬────────────────────────────────────────┤
│ Step 2: README Template       │ Step 3: LICENSE (Optional)             │
│   ☑ Generate README.md        │   ☐ Add LICENSE file                   │
│   Template: [Basic ▼]         │   License Type: [MIT ▼]               │
│   [Preview Template]          │   [Preview License]                    │
├───────────────────────────────┴────────────────────────────────────────┤
│ Step 4: Git & GitHub                                                   │
│   ☑ Initialize Git (git init)   ☑ Publish to GitHub                   │
│   Privacy: ●Private ○Public                                            │
│   [Create Local Repo]  [Publish to GitHub]  [🚀 Publish Folder]       │
│                                 [⬆️ Push to Branch]                    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Installation

### Prerequisites

**Required:**
- Python 3.7 or higher
- Git 2.0 or higher
- Tkinter (included with standard Python on Windows)
- Windows (the token auto-scan uses `ctypes.windll` for drive detection)

**Optional:**
- GitHub Personal Access Token (for authenticated features — see [Token Setup](#-token-setup))

### Step 1: Verify Python

```bat
python --version
:: Should show: Python 3.7.x or higher
```

If Python is not installed, download from [python.org](https://www.python.org/).

### Step 2: Verify Git

```bat
git --version
:: Should show: git version 2.x.x
```

If Git is not installed, download from [git-scm.com](https://git-scm.com/).

### Step 3: Download GithubTool

```bat
git clone https://github.com/kindle15/githubtool.git
cd githubtool
```

### Step 4: Install Dependencies

```bat
pip install requests
```

### Step 5: Run

```bat
python gui.py
```

---

## 🔑 Token Setup

A GitHub Personal Access Token unlocks full features (private repos, starring,
publishing, and more). GithubTool detects the token automatically — no config
file to edit.

### How to Get a Token

1. Click **[🔑 Token]** in the toolbar — it opens the GitHub token page directly
2. Or go to: <https://github.com/settings/tokens>
3. Click **"Generate new token (classic)"**
4. Select scopes: `repo`, `delete_repo` (and `admin:org` if you use org repos)
5. Copy the token (starts with `ghp_`)

### Method 1: USB / Removable Drive (Recommended for Portability)

1. Create a plain text file named **exactly**: `PersonalAccessToken.txt`
2. Paste your token as the **only content** (no extra spaces or newlines)
3. Save the file to the **root** of any drive letter **D: through Z:**

   ```
   D:\PersonalAccessToken.txt
   E:\PersonalAccessToken.txt
   ```

4. GithubTool scans all drives D:–Z: automatically on startup and on every
   Refresh. Works with both USB flash drives and external hard drives.

> **Note:** The filename must be exactly `PersonalAccessToken.txt` — not
> `.github_token` or any other name.

### Method 2: Environment Variable (Cross-Platform)

Set the `GITHUB_TOKEN` or `GH_TOKEN` environment variable before launching:

**Windows (System Properties → Environment Variables):**

```
Variable name:  GITHUB_TOKEN
Variable value: ghp_your_token_here
```

**Windows (Command Prompt, current session only):**

```bat
set GITHUB_TOKEN=ghp_your_token_here
python gui.py
```

After setting the token, click **[Refresh]** or restart the app.

---

## 🚀 Quick Start

```bat
cd githubtool
python gui.py
```

### Without Token (Public Browse Mode)

- Tab 1 shows "Public Browse: kindle15" (configurable in Settings)
- Can view public repositories
- Limited to 60 API requests/hour
- Cannot star repos or publish to GitHub

### With Token (Full Access Mode)

- Tab 1 shows "My Repos"
- Can view private repositories
- 5,000 API requests/hour
- Can star/unstar, publish, fork, rename, delete repos

### Configure Default Browse User

1. Click **Settings → Configure Public Browse User**
2. Enter a GitHub username (e.g., `octocat`)
3. Click Save — that user's public repos appear in Tab 1 when no token is present

---

## 📖 Usage Guide

### Tab 0: Welcome
Getting started guide and feature overview. Shows token setup instructions and
what's new in each version.

### Tab 1: My Repos / Public Browse
View, search, filter, export, and act on repositories. The right panel shows
details for the selected repo and has three action tabs:

| Tab | Actions |
|-----|---------|
| ⭐ Actions | Open in Browser, Clone, Download ZIP, Star/Unstar |
| 🔧 Manage | Toggle Privacy (Public↔Private), Fork, Rename |
| ⚠️ Danger | Delete Repository |

### Tab 2: Organization Repos
Browse repositories belonging to a GitHub organization. Requires a token with
`read:org` scope.

### Tab 3: Starred Repos
Your starred repositories. Requires a token.

### Tab 4: Download From Others
Browse any GitHub user's or org's public repos. Download release assets,
source ZIP, or clone directly.

### Tab 5: Creation Lab

**New Repo Workflow:**
1. Fill in repo name, description, and parent folder
2. Choose README and LICENSE templates (optional)
3. Check "Initialize Git" and "Publish to GitHub" as needed
4. Click **[Create Local Repo]** then **[Publish to GitHub]**

**Publish Existing Folder:**
1. Pick an existing local folder in the Push to Branch section
2. Click **[🚀 Publish Folder]**
3. Confirm repo name, privacy, and contents
4. GithubTool handles `git init`, remote setup, commit, and push

**Push to Branch:**
- Push changes in an existing local git repo to a branch on GitHub

---

## 🏗️ Build and Packaging (Windows)

Build script: `GHbuild_exe.bat`

**Basic build** (preserve existing `ght.version`):

```bat
GHbuild_exe.bat 2.0.2
```

**Clean build** (stamp `ght.version` with git provenance):

```bat
GHbuild_exe.bat 2.0.2 --clean --stamp
```

- `--clean` removes previous `build/`, `dist/`, and `__pycache__`
- `--stamp` overwrites `ght.version` with version, build_time, git_commit, and git_branch

Output artifacts are copied to `dist\GithubTool_build\<version>\` and include
`ght.version` and the spec file.

---

## ✅ Testing Checklist

- **Startup** — run `python gui.py`; confirm no error dialog when requirements are met
- **Token (USB)** — place `PersonalAccessToken.txt` on a D:–Z: drive; verify token detected on startup
- **Token (Env)** — set `GITHUB_TOKEN`; verify token detected
- **Download flows** — test All releases and Latest only
- **Create & Upload** — test personal and org creation; verify safety check fires on existing repo name
- **Push to Branch** — pick a local git repo and push to an existing GitHub branch
- **Publish Existing Folder** — pick a plain folder; verify full init → create → push flow
- **Tabbed actions** — test ⭐ Actions, 🔧 Manage (Fork, Rename, Toggle Privacy), ⚠️ Danger (Delete)
- **Export** — export to CSV and TXT; verify formatting
- **Build** — run `GHbuild_exe.bat 2.0.2 --clean --stamp` and verify `dist\GithubTool_build\2.0.2`

---

## ❓ FAQ

**Q: Where is the token file?**
A: Create `PersonalAccessToken.txt` on any drive D:–Z: (root of the drive).
GithubTool scans those drives automatically. There is no home-directory file option.

**Q: Does this work on Linux or macOS?**
A: The drive scan uses `ctypes.windll` (Windows only). On Linux/macOS, use the
`GITHUB_TOKEN` environment variable instead.

**Q: Which token scopes do I need?**
A: `repo` for full repo access; `delete_repo` if you want to delete repos from
the GUI; `admin:org` for organization repos.

**Q: The app says "No token found" but I have a USB plugged in.**
A: Make sure the file is named exactly `PersonalAccessToken.txt` (capital P,
capital A, capital T) and is at the root of the drive (e.g., `E:\PersonalAccessToken.txt`).

---

## 📁 Project Structure

| File | Purpose |
|------|---------|
| `gui.py` | Main application entry point (Tkinter GUI) |
| `auth_token.py` | Token detection: scans D:–Z: for `PersonalAccessToken.txt`, then env vars |
| `download_core.py` | Fetch repos from GitHub API |
| `csv_core.py` | Export to CSV/TXT |
| `repo_create_core.py` | Create GitHub repositories via API |
| `network_utils.py` | Network connectivity helpers |
| `ght_config.json` | Persisted settings (window size, last tab, export format) |
| `ght.version` | Version/build metadata (stamped by build script) |
| `GithubTool.spec` | PyInstaller spec for building the EXE |
| `GHbuild_exe.bat` | Windows build wrapper |

---

## 📜 License

(c) kindle15 / 2026 — All rights reserved.

---

**Last Updated:** 2026-03-12
**Current Version:** 2.0.2
**Status:** Stable Release
