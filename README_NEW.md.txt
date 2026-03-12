# 🚀 GithubTool v2.0.0

**A comprehensive desktop application for managing GitHub repositories with safety-first design.**

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/kindle15/githubtool)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-proprietary-red.svg)](LICENSE)

---

## 📑 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Configuration](#-configuration)
- [FAQ](#-faq)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🛡️ Safety First
- **Pre-Publish Checks** - Verifies repo doesn't exist before creating on GitHub
- **Detailed Warnings** - Shows repo info (last update, size, branches) before any action
- **Safe Options** - Cancel, Add Remote Only, or View on GitHub first
- **No Data Loss** - Prevents accidental overwrites of existing repositories

### ⚡ Creation Lab
- **Local Repository Creation** - Create repos with professional structure
- **README Templates** - Basic, Detailed, and Minimal formats
- **LICENSE Templates** - MIT, GPL-3.0, Apache-2.0, BSD-3-Clause
- **Git Integration** - Automatic initialization and initial commit
- **GitHub Publishing** - Push directly to GitHub with one click

### 📊 Repository Management
- **My Repos Tab** - View and manage your repositories
- **Organization Repos** - Access team repositories
- **Starred Repos** - Quick access to favorites
- **Smart Public Browsing** - View any user's public repos without authentication

### ⭐ Star Management
- **Star/Unstar** - Manage favorites directly from GUI
- **Auto-Detect Status** - Shows current star state
- **Works Everywhere** - Available on all tabs (0-4)

### 📤 Export Tools
- **CSV Export** - Structured data format for spreadsheets
- **TXT Export** - Formatted, readable text with aligned columns
- **Batch Export** - Export entire repo lists at once
- **Smart Formatting** - Wrapped descriptions, sorted by name

### 📥 Download Tools
- **Download Repos** - Get source code as ZIP
- **Clone Repos** - One-click git clone with depth=1
- **Release Assets** - Download binaries and attachments
- **README Viewer** - Preview README files before downloading

### 🔍 Search & Filter
- **Real-time Search** - Find repos by name instantly
- **Advanced Filters** - Public/Private, Forks/Owned
- **Sorted Tables** - Click column headers to sort
- **Persistent Settings** - Remembers your preferences

### 📐 Optimized UI
- **Space-Efficient Layout** - Steps 2 & 3 side-by-side in Creation Lab
- **Resizable Diagnostics** - Drag divider to adjust console size
- **Unified Right Panel** - Consistent layout across all tabs
- **Rate Limit Display** - Always visible API usage monitor

---

## 📸 Screenshots

### Main Interface
┌────────────────────────────────────────────────────────────────────┐ │ File Settings Help │ ├────────────────────────────────────────────────────────────────────┤ │ Git: ✓ | Auth: ✓ | Token: ghp_***abc | Network: ✓ | Mode: Tools │ ├────────────────────────────────────────────────────────────────────┤ │ [Refresh] [Create] | Export: ○CSV ●TXT [Export] | Search: [____] │ ├───────────────────────────┬────────────────────────────────────────┤ │ Welcome | My Repos | Org │ GitHub API Rate Limit │ │ Repos | Starred | Download│ 4,850 / 5,000 remaining │ │ From Others | Creation Lab │ ████████████████░░ 97% │ │ │ [Refresh Rate Limit] │ │ ┌──────────────────────┐ │ │ │ │ Name | Private | Fork│ │ Repository Details │ │ │ repo1 | No | No │ │ Name: my-awesome-project │ │ │ repo2 | Yes | No │ │ Private: No │ │ │ repo3 | No | Yes │ │ Stars: ⭐ 42 │ │ └──────────────────────┘ │ │ │ │ ⭐ Actions │ │ │ [🌐 Open in Browser] │ │ │ [📥 Clone Selected] │ │ │ [📦 Download ZIP] │ │ │ [⭐ Star Repo] │ ├────────────────────────────┴───────────────────────────────────────┤ │ Diagnostics Console (drag divider above to resize ↕) │ │ 2026-02-16 10:23:45 - Fetched 42 repositories │ │ 2026-02-16 10:23:46 - Rate limit: 4,850/5,000 remaining │ └────────────────────────────────────────────────────────────────────┘

Code

### Creation Lab
┌────────────────────────────────────────────────────────────────────┐ │ ⚡ Creation Lab │ ├────────────────────────────────────────────────────────────────────┤ │ Step 1: Repository Details │ │ Repository Name: [my-awesome-project__________________] │ │ Description: [A cool new tool___________________] │ │ Parent Folder: [/home/user/projects] [Browse...] │ ├───────────────────────────────┬────────────────────────────────────┤ │ Step 2: README Template │ Step 3: LICENSE (Optional) │ │ ☑ Generate README.md │ ☐ Add LICENSE file │ │ Template: [Basic ▼] │ License Type: [MIT ▼] │ │ [Preview Template] │ [Preview License] │ └───────────────────────────────┴────────────────────────────────────┘ │ Step 4: Git & GitHub │ │ ☑ Initialize Git (git init) │ │ ☐ Publish to GitHub │ │ Privacy: ●Private ○Public │ ├────────────────────────────────────────────────────────────────────┤ │ [Create Local Repo] [Publish to GitHub] │ └────────────────────────────────────────────────────────────────────┘

Code

### Safety Warning Dialog
┌────────────────────────────────────────────────────────────────────┐ │ ⚠️ Repository Already Exists on GitHub! │ ├────────────────────────────────────────────────────────────────────┤ │ Repository: kindle15/my-awesome-project │ │ Status: Already exists with content │ │ Last updated: 2026-02-15 │ │ Last pushed: 2026-02-14 │ │ Size: 245 KB │ │ Default branch: main │ │ │ │ URL: https://github.com/kindle15/my-awesome-project │ │ │ │ This repository already exists and may contain data. │ │ Publishing now could cause conflicts or data loss. │ │ │ │ What would you like to do? │ │ │ │ [✅ Cancel (Safest)] [🔗 Add as Remote Only] [🌐 View GitHub] │ └────────────────────────────────────────────────────────────────────┘

Code

---

## 🔧 Installation

### Prerequisites

**Required:**
- Python 3.7 or higher
- Git 2.0 or higher
- Tkinter (usually included with Python)

**Optional:**
- GitHub Personal Access Token (for authenticated features)

### Step 1: Verify Python

```bash
python3 --version
# Should show: Python 3.7.x or higher
If Python is not installed:

Linux: sudo apt install python3
macOS: brew install python3
Windows: Download from python.org
Step 2: Verify Git
bash
git --version
# Should show: git version 2.x.x
If Git is not installed:

Linux: sudo apt install git
macOS: brew install git
Windows: Download from git-scm.com
Step 3: Verify Tkinter
bash
python3 -m tkinter
# Should open a test window
If Tkinter is not installed:

Linux: sudo apt install python3-tk
macOS: Included with Python
Windows: Included with Python
Step 4: Download GithubTool
bash
git clone https://github.com/kindle15/githubtool.git
cd githubtool
Step 5: Configure Token (Optional but Recommended)
Choose ONE method:

Option A: Flash Drive (Recommended for portability)
bash
# Create token file on flash drive
echo "ghp_your_token_here" > /path/to/flashdrive/.github_token
Option B: Environment Variable
bash
# Linux/macOS - Add to ~/.bashrc or ~/.zshrc
export GITHUB_TOKEN="ghp_your_token_here"

# Windows - System Properties > Environment Variables
# Add: GITHUB_TOKEN = ghp_your_token_here
Option C: Home Directory
bash
echo "ghp_your_token_here" > ~/.github_token
chmod 600 ~/.github_token  # Restrict permissions
How to get a GitHub token:

Go to https://github.com/settings/tokens
Click "Generate new token (classic)"
Select scopes: repo, user, admin:org (optional)
Copy the token (starts with ghp_)
Save using one of the methods above
🚀 Quick Start
1. Launch Application
bash
cd githubtool
python3 gui_3.py
2. First-Time Setup
Without Token (Public Browse Mode):

Tab 1 shows "Public Browse: kindle15"
Can view public repositories
Limited to 60 API requests/hour
Cannot star repos or publish to GitHub
With Token (Full Access Mode):

Tab 1 shows "My Repos"
Can view private repositories
5,000 API requests/hour
Can star/unstar repos
Can publish to GitHub
Configure Default User:

Click Settings > Configure Public Browse User
Enter GitHub username (e.g., octocat)
Click Save
This user's public repos will show in Tab 1 when no token is present
3. Explore Tabs
Tab 0: Welcome - Getting started guide and feature overview

Tab 1: My Repos - Your repositories (or public browse)

Tab 2: Organization Repos - Team repositories (requires token)

Tab 3: Starred - Your starred repositories (requires token)

Tab 4: Download From Others - Browse and download any user's repos

Tab 5: Creation Lab - Create new repositories with templates

📖 Usage Guide
Managing Your Repositories
View Repositories
Go to Tab 1 (My Repos)
Repositories load automatically on startup
Click column headers to sort
Use search box to filter by name
Search and Filter
Search by name:

Code
1. Type in search box (top right)
2. Press Enter
3. Table updates in real-time
Filter by type:

Code
1. Click "Filter" dropdown
2. Choose: All, Public, Private, Forks, Owned
3. Table updates automatically
Star/Unstar Repository
Code
1. Click on a repository in any table
2. Look at right panel (gray bordered area)
3. Find "⭐ Actions" section
4. Click [☆ Star Repo] or [⭐ Unstar Repo]
5. Status updates immediately
Export Repository List
Export to CSV:

Code
1. Select "CSV" radio button (top bar)
2. Click "Export View"
3. Choose save location
4. File saved with format:
   Repo, Owned/Cloned, Private/Public, Description
Export to TXT:

Code
1. Select "TXT" radio button (top bar)
2. Click "Export View"
3. Choose save location
4. File saved with aligned columns and wrapped descriptions
Creating New Repositories
Step-by-Step Workflow
1. Navigate to Creation Lab

Click Tab 5 (Creation Lab)
2. Fill Repository Details

Code
- Repository Name: my-awesome-project (required)
- Description: A cool new tool (optional)
- Parent Folder: /home/user/projects (click Browse to change)
3. Choose README Template

Code
☑ Generate README.md
Template: [Basic / Detailed / Minimal]
[Preview Template] - Click to see in Diagnostics
README Templates:

Basic: Name, Description, Installation, Usage, Contributing, License
Detailed: + Table of Contents, Features, Tests
Minimal: Name, Description, Usage only
4. Add LICENSE (Optional)

Code
☑ Add LICENSE file
License Type: [MIT / GPL-3.0 / Apache-2.0 / BSD-3-Clause]
[Preview License] - Click to see in Diagnostics
5. Configure Git & GitHub

Code
☑ Initialize Git (git init) - Recommended
☐ Publish to GitHub - Optional (requires token)
  Privacy: ●Private ○Public
6. Create Repository

Code
Click: [Create Local Repo]

Expected output in Diagnostics:
✓ Created folder: /home/user/projects/my-awesome-project
✓ Generated README.md (Basic template)
✓ Generated LICENSE (MIT)
✓ Initialized Git repository
✓ Created initial commit
✅ Repository created successfully!
7. Publish to GitHub (Optional)

Code
If "Publish to GitHub" was checked:
Click: [Publish to GitHub]

Safety Check Runs:
- Checks if repo exists on GitHub
- Shows warning if it does
- Proceeds if it doesn't

Success output:
✓ Created GitHub repository: https://github.com/user/repo
✓ Added remote origin
✓ Pushed to GitHub
✅ Published successfully!
🌐 Opens in browser automatically
Downloading Repositories
From Tab 4 (Download From Others)
1. Enter Repository Information

Code
Format options:
- owner/repo (e.g., octocat/Hello-World)
- owner/ or owner (e.g., octocat/)
- Multiple, comma-separated (e.g., user1/repo1, user2/repo2)
2. Click "Fetch"

Code
- Repository tree appears on left
- Click repository to view details
- README appears in center panel
- Properties appear on right
3. Download Options

Option A: Clone with Git

Code
1. Select repository in tree
2. Click "Clone Repo" at bottom
3. Choose destination folder
4. Repository clones with: git clone --depth 1
Option B: Download as ZIP

Code
1. Select repository in tree
2. Click "Download Source Zip" at bottom
3. Enter branch name (or leave blank for default)
4. Choose save location
5. ZIP file downloads
Option C: Download Release Assets

Code
1. Expand repository in tree
2. Click on a release
3. Assets appear in "Release Assets" panel
4. Select asset(s)
5. Click "Download Selected Asset(s)"
6. Choose save location
Using Right Panel Actions
Available on ALL tabs (0-5)!

🌐 Open in Browser
Code
1. Select repository
2. Click [🌐 Open in Browser]
3. Opens GitHub page in default browser
📥 Clone Selected
Code
1. Select repository
2. Click [📥 Clone Selected]
3. Choose destination folder
4. Repository clones with git
📦 Download ZIP
Code
1. Select repository
2. Click [📦 Download ZIP]
3. Enter branch (or blank for default)
4. Choose save location
5. Downloads source archive
⭐ Star Repo
Code
1. Select repository
2. Button shows current state:
   - [☆ Star Repo] if not starred
   - [⭐ Unstar Repo] if starred
3. Click to toggle
4. Status updates immediately
⚙️ Configuration
Configuration File
Location: ght_config.json (same directory as gui_3.py)

Format:

JSON
{
  "default_public_user": "kindle15",
  "last_tab": 0,
  "window_geometry": "1200x700",
  "export_format": "txt"
}
Configuration Options
Key	Type	Default	Description
default_public_user	string	"kindle15"	Username shown in Tab 1 when no token
last_tab	integer	0	Last active tab (0-5)
window_geometry	string	"1200x700"	Window size (WIDTHxHEIGHT)
export_format	string	"txt"	Default export format ("csv" or "txt")
Manual Configuration
Edit config file:

bash
nano ght_config.json
Example customizations:

Change default user:

JSON
{
  "default_public_user": "octocat"
}
Set default window size:

JSON
{
  "window_geometry": "1600x900"
}
Set default export format:

JSON
{
  "export_format": "csv"
}
Configuration is auto-saved on exit.

❓ FAQ
General Questions
Q: Do I need a GitHub token?

A: No, but highly recommended!

Without token:

✅ View public repositories
✅ Browse any user's public repos
✅ Download repos/releases
✅ Export data
❌ View private repos
❌ Star/unstar repos
❌ Publish to GitHub
⚠️ Limited to 60 API requests/hour
With token:

✅ All features above PLUS
✅ View your private repositories
✅ Star/unstar repositories
✅ Publish to GitHub
✅ 5,000 API requests/hour
Q: Is my GitHub token safe?

A: Yes! Your token is:

✅ Only stored locally (flash drive, env, or home directory)
✅ Never logged in full (masked: ghp_abc...xyz)
✅ Never sent anywhere except GitHub API
✅ Read with restricted permissions (600)
✅ Not included in exports or screenshots
Best practices:

Use fine-grained tokens (not classic)
Set expiration dates
Only grant necessary permissions (repo, user)
Revoke immediately if compromised
Q: What operating systems are supported?

A: GithubTool works on:

✅ Linux (Ubuntu 20.04+, Debian, Fedora, etc.)
✅ macOS (11+ Big Sur and newer)
✅ Windows (10+)
Tkinter is cross-platform, so it should work on any system with Python 3.7+.

Q: Can I use this offline?

A: Partially.

Offline capabilities:

✅ View previously loaded repositories (stays in memory)
✅ Export previously loaded data
✅ Create local repositories (Creation Lab)
✅ Use README/LICENSE templates
❌ Fetch new repository data (requires internet)
❌ Publish to GitHub (requires internet)
❌ Star/unstar repos (requires internet)
Future enhancement: Database caching for full offline access.

Q: How do I update to the latest version?

A:

bash
cd githubtool
git fetch origin
git checkout v2.0.0  # or latest version
# or simply
git pull origin main
Your ght_config.json is preserved during updates.

Q: Can I use this with GitHub Enterprise?

A: Yes! Set the API base URL:

bash
export GITHUB_API_URL="https://github.company.com/api/v3"
python3 gui_3.py
Note: Requires code modification. See DEVELOPER.md for details.

Feature Questions
Q: How do I publish an existing local repo to GitHub?

A: Currently, Creation Lab only publishes repos it creates. For existing repos:

bash
cd /path/to/existing/repo
git remote add origin https://github.com/user/repo.git
git push -u origin main
Future enhancement: Add "Publish Existing Repo" feature.

Q: Can I star repositories in bulk?

A: Not currently. You must star one at a time:

Select repo
Click [☆ Star Repo]
Future enhancement: Multi-select star/unstar.

Q: Can I manage pull requests or issues?

A: Not in v2.0.0. This version focuses on repository management.

Planned for v2.2.0: Pull request and issue management.

Q: How do I change the README template after creation?

A: Edit the README.md file manually in your text editor.

Templates are only applied during initial creation.

Q: Can I add custom README templates?

A: Yes! See DEVELOPER.md for instructions on modifying README_TEMPLATES.

🛠️ Troubleshooting
Installation Issues
Problem: "python3: command not found"

Solution:

bash
# Try 'python' instead
python --version

# Or install Python
# Linux: sudo apt install python3
# macOS: brew install python3
# Windows: Download from python.org
Problem: "No module named '_tkinter'"

Solution:

bash
# Linux
sudo apt install python3-tk

# macOS
# Tkinter included with Python
# If missing, reinstall Python from python.org

# Windows
# Tkinter included with Python
# Reinstall Python and check "tcl/tk" option
Problem: "git: command not found"

Solution:

bash
# Linux
sudo apt install git

# macOS
brew install git

# Windows
# Download from: https://git-scm.com/download/win
Token Issues
Problem: "Token not found" on startup

Solutions:

Check token file exists:

bash
ls -la ~/.github_token
# Should show: -rw------- 1 user user 41 ...
Check token format:

bash
cat ~/.github_token
# Should start with: ghp_
Check file permissions:

bash
chmod 600 ~/.github_token
Verify token is valid:

bash
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
# Should return your GitHub user info
Problem: "Rate limit exceeded"

Solutions:

Check rate limit:

Look at right panel "GitHub API Rate Limit"
Shows remaining requests and reset time
With token: 5,000/hour Without token: 60/hour

Wait for reset:

Note the "Resets at:" time
Wait until specified time
Or use a token to get 5,000/hour
Application Issues
Problem: Window too small or diagnostics not visible

Solutions:

Resize window:

Drag window corners to resize
Recommended minimum: 1200x700
Drag diagnostics divider:

Hover over line between main area and diagnostics
Cursor changes to resize ↕
Click and drag down
Reset config:

bash
rm ght_config.json
# Restart app - defaults to 1200x700
Problem: "Repository already exists" when publishing

This is actually a FEATURE (safety check)!

What it means:

A repo with this name already exists on GitHub
Publishing would cause conflicts
Options presented:

1. Cancel (Safest)

Aborts publishing
No changes made
Rename local repo and try again
2. Add as Remote Only

Links local repo to existing GitHub repo
Doesn't create new repo
Allows manual merge later
3. View on GitHub

Opens existing repo in browser
Inspect before deciding
Can delete GitHub repo if safe
Problem: Git operations fail

Solutions:

Verify git is installed:

bash
git --version
# Should show: git version 2.x.x
Check git configuration:

bash
git config --global user.name
git config --global user.email

# If not set:
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
Check folder permissions:

bash
ls -la /path/to/parent/folder
# Should be writable by your user
Problem: Export fails with Unicode errors

This should be fixed in v2.0.0, but if it occurs:

Check system encoding:

bash
python3 -c "import sys; print(sys.getdefaultencoding())"
# Should show: utf-8
Set UTF-8 encoding:

bash
# Add to ~/.bashrc or ~/.zshrc
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
Problem: Network connectivity errors

Solutions:

Check internet connection:

bash
ping 8.8.8.8
Check GitHub is accessible:

bash
curl https://api.github.com
# Should return JSON response
Check firewall:

Allow HTTPS (port 443) to api.github.com
Check corporate firewall settings
Use proxy (if required):

bash
export HTTPS_PROXY=http://proxy.company.com:8080
Problem: Right panel not visible

This was fixed in Drop 3.3, but if it occurs:

Solution:

Update to latest version (v2.0.0)
Right panel now uses grid layout (always visible)
Gray border shows location
Problem: Application won't start

Check Python version:

bash
python3 --version
# Must be 3.7 or higher
Check for syntax errors:

bash
python3 -m py_compile gui_3.py
# Should complete without errors
Check dependencies:

bash
python3 -c "import tkinter"
# Should complete without errors
Run with error output:

bash
python3 gui_3.py 2>&1 | tee error.log
# Check error.log for details
🤝 Contributing
We welcome contributions! See DEVELOPER.md for detailed guidelines.

Quick Start for Contributors
1. Fork and clone:

bash
git clone https://github.com/YOUR_USERNAME/githubtool.git
cd githubtool
2. Create feature branch:

bash
git checkout -b feature/my-new-feature
3. Make changes and test:

bash
# Make your changes
python3 gui_3.py  # Test locally
4. Commit with clear message:

bash
git add .
git commit -m "feat(scope): add new feature description"
5. Push and create pull request:

bash
git push origin feature/my-new-feature
# Create PR on GitHub
Commit Message Format
Code
<type>(<scope>): <subject>

<body>

<footer>
Types: feat, fix, docs, style, refactor, test, chore

Example:

Code
feat(creation-lab): add Python .gitignore template

- Add Python-specific .gitignore template
- Include common Python patterns (venv, __pycache__, etc.)
- Add checkbox to Creation Lab UI

Closes #123
📄 License
GithubTool v2.0.0

(c) kindle15 / 2026

All rights reserved.

This software is proprietary. Contact kindle15 for licensing information.

🙏 Acknowledgments
Built with:

Python 3.7+
Tkinter (Python's GUI framework)
GitHub REST API
Inspired by:

GitHub Desktop
GitKraken
Visual Studio Code's Git integration
Thanks to:

GitHub for excellent API documentation
Python community for best practices
All contributors and testers
📞 Support
Need help?

Check this README
Check DEVELOPER.md for technical details
Check FAQ section
Check Troubleshooting section
Search GitHub Issues
Create new issue with:
Error message
Steps to reproduce
Python version (python3 --version)
OS version
Token source (don't include actual token!)
Project Links:

GitHub: https://github.com/kindle15/githubtool
Issues: https://github.com/kindle15/githubtool/issues
Wiki: https://github.com/kindle15/githubtool/wiki
Releases: https://github.com/kindle15/githubtool/releases
🗺️ Roadmap
v2.1.0 - Enhanced Search

Fuzzy search
Search by language
Date range filters
v2.2.0 - Collaboration

Pull request management
Issue tracking
Team viewer
v2.3.0 - Analytics

Commit graphs
Language charts
Star growth tracking
v3.0.0 - Major Rewrite

Plugin system
Custom themes
Multi-account support
Database caching
See DEVELOPER.md for complete roadmap.

📊 Statistics
Code:

~2,500 lines of Python
6 tabs with unique functionality
50+ functions and methods
15+ custom widgets
Features:

2 authentication modes (with/without token)
3 README templates
4 LICENSE templates
2 export formats
Unlimited public repo browsing
Supported:

3 operating systems (Linux, macOS, Windows)
100+ GitHub API endpoints
5,000 API requests/hour (with token)
📝 Changelog Summary
Version	Date	Highlights
v2.0.0	Feb 2026	🛡️ Safety checks, prevent data loss
v1.7.0	Feb 2026	📐 Space-efficient layout
v1.6.0	Feb 2026	⚡ Creation Lab with templates
v1.5.0	Feb 2026	🎨 Unified layout across tabs
v1.3.0	Feb 2026	⭐ Star/unstar functionality
v1.2.0	Feb 2026	📤 Export to CSV/TXT
v1.0.0	Feb 2026	🎉 Initial release
See CHANGELOG.md for detailed version history.

Made with ❤️ by kindle15

GithubTool - Manage GitHub repositories with confidence and safety.