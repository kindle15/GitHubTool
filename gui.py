#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gui.py - GithubTool GUI with Smart Public Browsing, Export, and Star Repos
Version: 2.0.2

Changelog:
- Drop 1: Welcome tab, smart public browsing, settings system
- Drop 2: CSV/TXT export, README viewer, enhanced properties, owned/cloned detection
- Drop 2.1: Fixed export width bug, added Tab 4 export support
- Drop 3: Rate limit display in Tab 4, Star/Unstar repos functionality
- Drop 3.1: Fixed diagnostics panel squishing bug (resizable with PanedWindow)
- Drop 3.2: Attempted pack layout fix
- Drop 3.3: GRID LAYOUT - FORCE RIGHT PANEL VISIBLE
- Drop 3.4: Fixed initialization order bug
- Drop 3.5: Removed old rate limit from Tab 4, unified layout with main right panel
- Drop 3.6: Added Tab 5 "Creation Lab" - Local repo creator with templates and GitHub publish
- Drop 3.7: Space-efficient layout - Steps 2 & 3 side-by-side in Creation Lab
- Drop 3.8/v2.0.0: Safety checks before publishing (prevent overwrites) + Copyright in About
- v2.0.1: Push to Branch feature, Download ZIP fix, Delete repo, Creation Lab branding
- v2.0.2: Tabbed action panel (⭐/🔧/⚠️), Token button, Stats button, Toggle Privacy,
          Fork Repo, Rename Repo - all output to console (no popup spam)
"""
# ============================================================================
# IMPORTS
# ============================================================================
from __future__ import annotations
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import subprocess
import webbrowser
import time
import json
import urllib.request
import urllib.error
import csv
import textwrap
from typing import List, Dict, Optional, Callable, Any, Tuple
from datetime import datetime
from pathlib import Path

# Project-specific imports (must exist in same project)
from auth_token import get_token
from csv_core import export_repos_to_txt
from download_core import fetch_user_repos, GitHubFetchError

# Optional modules
try:
    import repo_create_core
except Exception:
    repo_create_core = None

try:
    import network_utils
except Exception:
    network_utils = None



# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================
APP_TITLE = "GithubTool v2.0.2"
DEFAULT_MODE = "Repository Tools"
CONFIG_FILE = "ght_config.json"

# Columns for table
COLUMNS = ("name", "private", "fork", "full_name", "html_url")
COLUMN_HEADINGS = {
    "name": "Name",
    "private": "Private",
    "fork": "Fork",
    "full_name": "Owner/Repo",
    "html_url": "URL",
}

# Default configuration
DEFAULT_CONFIG = {
    "default_public_user": "kindle15",
    "last_tab": 0,
    "window_geometry": "1200x700",
    "export_format": "txt"
}

# README Templates (NEW IN DROP 3.6)
README_TEMPLATES = {
    "Basic": """# {REPO_NAME}

## Description
-

## Installation
-

## Usage
-

## Contributing
-

## License
-
""",
    "Detailed": """# {REPO_NAME}

{DESCRIPTION}

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Installation
-

## Usage
-

## Features
-

## Contributing
-

## Tests
-

## License
-
""",
    "Minimal": """# {REPO_NAME}

{DESCRIPTION}

## Usage
-
"""
}

# LICENSE Templates (NEW IN DROP 3.6)
LICENSE_TEMPLATES = {
    "MIT": """MIT License

Copyright (c) {YEAR} {AUTHOR}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",
    "GPL-3.0": """GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) {YEAR} {AUTHOR}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
""",
    "Apache-2.0": """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Copyright {YEAR} {AUTHOR}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
""",
    "BSD-3-Clause": """BSD 3-Clause License

Copyright (c) {YEAR}, {AUTHOR}

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
}


# ============================================================================
# MODULE: ConfigManager
# Description: Handles application configuration persistence
# Drop: Added in Drop 1
# ============================================================================
class ConfigManager:
    """Manages application configuration persistence."""
    
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load config from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults (in case new keys added)
                    config = DEFAULT_CONFIG.copy()
                    config.update(loaded)
                    return config
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()
    
    def save_config(self) -> None:
        """Save current config to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set config value and save."""
        self.config[key] = value
        self.save_config()


# ============================================================================
# MODULE: Helper Functions
# Description: Utility functions for token masking, diagnostics, HTTP requests
# Drop: Added in Drop 1
# ============================================================================
def _mask_token(token: str) -> str:
    """Mask sensitive token for display."""
    if not token:
        return "None"
    t = token.strip()
    if len(t) <= 12:
        return t
    return f"{t[:6]}...{t[-4:]}"

def _append_diag_widget(widget: tk.Text, text: str) -> None:
    """Append a timestamped line to the diagnostics text widget in a thread-safe way."""
    try:
        if widget is None:
            return
        def _do():
            try:
                widget.configure(state="normal")
                widget.insert("end", f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {text}\n")
                widget.see("end")
                widget.configure(state="disabled")
            except Exception:
                pass
        try:
            widget.after(0, _do)
        except Exception:
            _do()
    except Exception:
        pass

def _http_get_json(url: str, token: Optional[str], timeout: int = 10) -> Tuple[Any, Dict[str, str]]:
    """Make HTTP GET request and parse JSON response."""
    headers = {"User-Agent": "GithubTool/2.0.2"}
    if token:
        headers["Authorization"] = f"token {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        hdrs = {k: v for k, v in resp.getheaders()}
        return data, hdrs


# ============================================================================
# MODULE: GitHub Star Management (NEW IN DROP 3)
# Description: Functions for starring/unstarring repos on GitHub
# Drop: Added in Drop 3
# ============================================================================
def check_if_starred(owner: str, repo: str, token: str) -> bool:
    """
    Check if a repository is starred by the authenticated user.
    
    Args:
        owner: Repository owner
        repo: Repository name
        token: GitHub API token
    
    Returns:
        True if starred, False if not starred
    
    Raises:
        Exception: If API call fails
    """
    url = f"https://api.github.com/user/starred/{owner}/{repo}"
    headers = {
        "User-Agent": "GithubTool/2.0.2",
        "Authorization": f"token {token}"
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            # 204 = starred, 404 = not starred
            return resp.status == 204
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise

def star_repository(owner: str, repo: str, token: str) -> bool:
    """
    Star a repository on GitHub.
    
    Args:
        owner: Repository owner
        repo: Repository name
        token: GitHub API token
    
    Returns:
        True if successful
    
    Raises:
        Exception: If API call fails
    """
    url = f"https://api.github.com/user/starred/{owner}/{repo}"
    headers = {
        "User-Agent": "GithubTool/2.0.2",
        "Authorization": f"token {token}",
        "Content-Length": "0"
    }
    
    req = urllib.request.Request(url, headers=headers, method='PUT')
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status == 204

def unstar_repository(owner: str, repo: str, token: str) -> bool:
    """
    Unstar a repository on GitHub.
    
    Args:
        owner: Repository owner
        repo: Repository name
        token: GitHub API token
    
    Returns:
        True if successful
    
    Raises:
        Exception: If API call fails
    """
    url = f"https://api.github.com/user/starred/{owner}/{repo}"
    headers = {
        "User-Agent": "GithubTool/2.0.2",
        "Authorization": f"token {token}"
    }
    
    req = urllib.request.Request(url, headers=headers, method='DELETE')
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status == 204


# ============================================================================
# MODULE: GitHub Repository Management (ENHANCED IN DROP 3.8)
# Description: Functions for creating repos and checking existence
# Drop: Added in Drop 3.6, Enhanced in Drop 3.8 (safety checks)
# ============================================================================
def check_if_repo_exists(owner: str, repo_name: str, token: str) -> Tuple[bool, Optional[Dict]]:
    """
    Check if a repository already exists on GitHub.
    
    Args:
        owner: Repository owner (username)
        repo_name: Repository name
        token: GitHub API token
    
    Returns:
        Tuple of (exists: bool, repo_data: Optional[Dict])
        - If repo exists: (True, repo_data)
        - If repo doesn't exist: (False, None)
    
    Raises:
        Exception: If API call fails (other than 404)
    
    Added in: Drop 3.8/v2.0.0
    """
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    headers = {
        "User-Agent": "GithubTool/2.0.2",
        "Authorization": f"token {token}"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return True, data  # Repo exists
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, None  # Repo doesn't exist (this is OK)
        raise  # Other error - propagate it

def get_authenticated_user(token: str) -> str:
    """
    Get the authenticated user's username.
    
    Args:
        token: GitHub API token
    
    Returns:
        Username of authenticated user
    
    Raises:
        Exception: If API call fails
    
    Added in: Drop 3.8/v2.0.0
    """
    url = "https://api.github.com/user"
    headers = {
        "User-Agent": "GithubTool/2.0.2",
        "Authorization": f"token {token}"
    }
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        return data.get("login", "")

def create_github_repository(name: str, description: str, private: bool, token: str) -> Dict:
    """
    Create a new repository on GitHub.
    
    Args:
        name: Repository name
        description: Repository description
        private: Whether repo should be private
        token: GitHub API token
    
    Returns:
        Repository data dict from GitHub API
    
    Raises:
        Exception: If API call fails
    """
    url = "https://api.github.com/user/repos"
    headers = {
        "User-Agent": "GithubTool/2.0.2",
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "name": name,
        "description": description,
        "private": private,
        "auto_init": False  # We'll push our own initial commit
    }
    
    req = urllib.request.Request(
        url, 
        data=json.dumps(data).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


# ============================================================================
# MODULE: ExportManager
# Description: Handles CSV and TXT export with formatting
# Drop: Added in Drop 2, Fixed in Drop 2.1 (width calculation bug)
# ============================================================================
class ExportManager:
    """Handles exporting repository data to CSV and TXT formats."""
    
    @staticmethod
    def _is_owned(repo: Dict) -> str:
        """
        Determine if repo is owned (original) or cloned (forked).
        
        Returns: "Owned" or "Cloned"
        """
        return "Cloned" if repo.get("fork", False) else "Owned"
    
    @staticmethod
    def _get_privacy(repo: Dict) -> str:
        """Get privacy status of repo."""
        return "Private" if repo.get("private", False) else "Public"
    
    @staticmethod
    def _wrap_description(desc: str, width: int = 80, indent: str = "  ") -> str:
        """
        Wrap description text with 2-space indent on continuation lines.
        
        Args:
            desc: Description text to wrap
            width: Maximum line width (must be > 0)
            indent: Indent string for wrapped lines (default: 2 spaces)
        
        Returns: Wrapped text with indentation
        
        Fixed in: Drop 2.1 (ensure width is always positive)
        """
        if not desc:
            return ""
        
        # Ensure width is at least 20 characters
        width = max(20, width)
        
        # Use textwrap to wrap the description
        lines = textwrap.wrap(desc, width=width, 
                             subsequent_indent=indent,
                             break_long_words=False,
                             break_on_hyphens=False)
        return "\n".join(lines)
    
    @staticmethod
    def export_to_csv(repos: List[Dict], filepath: str) -> None:
        """
        Export repositories to CSV format.
        
        Columns: Repo | Owned/Cloned | Private/Public | Description
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(["Repo", "Owned/Cloned", "Private/Public", "Description"])
            
            # Sort by repo name
            sorted_repos = sorted(repos, key=lambda r: (r.get("full_name") or "").lower())
            
            # Data rows
            for repo in sorted_repos:
                name = repo.get("full_name", repo.get("name", "Unknown"))
                owned = ExportManager._is_owned(repo)
                privacy = ExportManager._get_privacy(repo)
                desc = repo.get("description") or ""
                
                writer.writerow([name, owned, privacy, desc])
    
    @staticmethod
    def export_to_txt(repos: List[Dict], filepath: str) -> None:
        """
        Export repositories to formatted TXT.
        
        Format: Aligned columns with wrapped descriptions
        
        Fixed in: Drop 2.1 (width calculation bug)
        """
        # Sort by repo name
        sorted_repos = sorted(repos, key=lambda r: (r.get("full_name") or "").lower())
        
        if not sorted_repos:
            # Handle empty list
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("No repositories to export.\n")
            return
        
        # Calculate column widths
        max_name = max(len(r.get("full_name", r.get("name", ""))) for r in sorted_repos)
        max_name = max(max_name, len("Repo Name"))
        max_name = min(max_name, 50)
        
        owned_width = 12
        privacy_width = 14
        
        # Calculate description width (with minimum of 30 characters)
        total_fixed = max_name + owned_width + privacy_width + 9
        desc_width = max(30, 120 - total_fixed)
        
        # Build output
        lines = []
        
        # Header
        header = f"{'Repo Name':<{max_name}} | {'Owned/Cloned':<{owned_width}} | {'Private/Public':<{privacy_width}} | Description"
        lines.append(header)
        lines.append("-" * min(len(header), 120))
        
        # Data rows
        for repo in sorted_repos:
            name = repo.get("full_name", repo.get("name", "Unknown"))
            if len(name) > max_name:
                name = name[:max_name-3] + "..."
            
            owned = ExportManager._is_owned(repo)
            privacy = ExportManager._get_privacy(repo)
            desc = repo.get("description") or ""
            
            wrapped_desc = ExportManager._wrap_description(desc, width=desc_width)
            
            desc_lines = wrapped_desc.split('\n') if wrapped_desc else [""]
            first_line = f"{name:<{max_name}} | {owned:<{owned_width}} | {privacy:<{privacy_width}} | {desc_lines[0]}"
            lines.append(first_line)
            
            for desc_line in desc_lines[1:]:
                continuation = f"{'':<{max_name}} | {'':<{owned_width}} | {'':<{privacy_width}} | {desc_line}"
                lines.append(continuation)
        
        # Footer
        lines.append("")
        lines.append(f"Total repositories: {len(sorted_repos)}")
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))


# ============================================================================
# MODULE: RepoTable Widget
# Description: Treeview table for displaying repository lists
# Drop: Added in Drop 1
# ============================================================================
class RepoTable(ttk.Frame):
    """A table showing repositories using ttk.Treeview."""

    def set_dynamic_height(self, available_pixels: int, row_height: int = 24, fraction: float = 0.5) -> None:
        """Dynamically adjust table height based on available space."""
        try:
            if fraction <= 0 or fraction > 1:
                fraction = 0.5
            usable = int(available_pixels * fraction)
            rows = max(3, int(usable / max(1, row_height)))
            self.tree.configure(height=rows)
        except Exception:
            pass

    def __init__(self, master):
        super().__init__(master)
        self.tree = ttk.Treeview(self, columns=COLUMNS, show="headings", selectmode="extended")
        for col in COLUMNS:
            self.tree.heading(col, text=COLUMN_HEADINGS.get(col, col),
                              command=lambda c=col: self._sort_by(c, False))
            self.tree.column(col, width=180 if col == "name" else 100, anchor="w")
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def clear(self) -> None:
        """Clear all items from the table."""
        for i in self.tree.get_children():
            self.tree.delete(i)

    def populate(self, repos: List[Dict]) -> None:
        """Populate table with repository data."""
        self.clear()
        for r in repos:
            vals = (
                r.get("name", ""),
                "Yes" if r.get("private", False) else "No",
                "Yes" if r.get("fork", False) else "No",
                r.get("full_name", ""),
                r.get("html_url", ""),
            )
            self.tree.insert("", "end", values=vals, tags=(str(r.get("id", "")),))

    def selected_items(self) -> List[List[Any]]:
        """Get currently selected items."""
        return [self.tree.item(i)["values"] for i in self.tree.selection()]

    def all_items(self) -> List[List[Any]]:
        """Get all items in the table."""
        return [self.tree.item(i)["values"] for i in self.tree.get_children()]

    def _sort_by(self, col: str, descending: bool) -> None:
        """Sort table by column."""
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        try:
            data.sort(reverse=descending, key=lambda t: t[0].lower() if isinstance(t[0], str) else t[0])
        except Exception:
            data.sort(reverse=descending, key=lambda t: t[0])
        for index, (_, item) in enumerate(data):
            self.tree.move(item, '', index)
        self.tree.heading(col, command=lambda c=col: self._sort_by(c, not descending))


# ============================================================================
# MODULE: RateLimitWidget (NEW IN DROP 3)
# Description: Reusable rate limit display widget
# Drop: Added in Drop 3
# ============================================================================
class RateLimitWidget(ttk.LabelFrame):
    """
    Reusable widget for displaying GitHub API rate limit information.
    
    Added in: Drop 3
    """
    
    def __init__(self, master, diag_append: Optional[Callable[[str], None]] = None):
        super().__init__(master, text="GitHub API Rate Limit")
        self.diag_append = diag_append or (lambda x: None)
        
        self.rate_limit_label = ttk.Label(self, text="Checking...", font=("TkDefaultFont", 9))
        self.rate_limit_label.pack(padx=8, pady=4)
        
        self.rate_limit_progress = ttk.Progressbar(self, mode="determinate", length=200)
        self.rate_limit_progress.pack(padx=8, pady=4)
        
        self.rate_limit_detail = ttk.Label(self, text="", font=("TkDefaultFont", 8))
        self.rate_limit_detail.pack(padx=8, pady=4)
        
        refresh_btn = ttk.Button(self, text="Refresh Rate Limit", command=self.refresh_async)
        refresh_btn.pack(padx=8, pady=4)
    
    def refresh_async(self) -> None:
        """Refresh rate limit asynchronously."""
        threading.Thread(target=self.refresh, daemon=True).start()
    
    def refresh(self) -> None:
        """Fetch and display current GitHub API rate limit."""
        try:
            token, _ = get_token()
            url = "https://api.github.com/rate_limit"
            data, _ = _http_get_json(url, token)
            
            core = data.get('resources', {}).get('core', {})
            limit = core.get('limit', 0)
            used = core.get('used', 0)
            remaining = core.get('remaining', 0)
            reset_timestamp = core.get('reset', 0)
            
            reset_time = datetime.fromtimestamp(reset_timestamp).strftime('%H:%M:%S') if reset_timestamp else "Unknown"
            
            if limit > 0:
                pct = int((remaining / limit) * 100)
                self.rate_limit_label.config(text=f"{remaining:,} / {limit:,} requests remaining")
                self.rate_limit_progress['value'] = pct
                self.rate_limit_detail.config(text=f"Used: {used:,} | Resets at: {reset_time}")
                
                if remaining < 100:
                    self.rate_limit_label.config(foreground="red")
                elif remaining < 500:
                    self.rate_limit_label.config(foreground="orange")
                else:
                    self.rate_limit_label.config(foreground="green")
                
                self.diag_append(f"Rate limit: {remaining}/{limit} remaining (resets at {reset_time})")
            else:
                self.rate_limit_label.config(text="Rate limit info unavailable")
                self.rate_limit_progress['value'] = 0
        except Exception as e:
            self.rate_limit_label.config(text="Failed to fetch rate limit")
            self.rate_limit_detail.config(text=f"Error: {str(e)[:40]}")
            self.diag_append(f"Rate limit check failed: {e}")

# ============================================================================
# MODULE: WelcomeTab
# Description: Welcome/Info tab with getting started guide
# Drop: Added in Drop 1, Enhanced in Drop 2, Updated in Drop 3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, v2.0.0
# ============================================================================
class WelcomeTab(ttk.Frame):
    """Welcome and information tab with getting started guide."""
    
    def __init__(self, master):
        super().__init__(master)
        
        # Create main canvas for scrolling
        canvas = tk.Canvas(self, bg='white')
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Content
        content = scrollable_frame
        
        # Main Title
        title = ttk.Label(content, text="GITHUBTOOL", 
                         font=("TkDefaultFont", 24, "bold"))
        title.pack(pady=(30, 10))
        
        # Version subtitle
        version = ttk.Label(content, text="Version 2.0.2", 
                           font=("TkDefaultFont", 10, "italic"))
        version.pack(pady=(0, 10))
        
        # Scroll instruction
        scroll_hint = ttk.Label(content, text="👇 Scroll down to see more info 👇", 
                               font=("TkDefaultFont", 11, "bold"),
                               foreground="#0066cc")
        scroll_hint.pack(pady=(10, 30))
        
        # Separator
        separator1 = ttk.Separator(content, orient="horizontal")
        separator1.pack(fill="x", padx=40, pady=10)
        
        # Getting Started Section
        # Getting Started Section
        self._add_section(content, "🚀 Getting Started", """
GithubTool helps you manage GitHub repositories with ease.

WITHOUT TOKEN (Public Browse):
• Browse any user's public repositories
• No authentication required
• Limited to public repos only

WITH TOKEN (Full Access):
• Access your private repositories
• Star/unstar repos on GitHub ⭐
• Create repos, full API access
• 5,000 API requests per hour (vs 60 without token)

HOW TO SET UP A TOKEN:
1. Click [🔑 Token] button in the toolbar
2. GitHub token page will open
3. Select scopes: repo + delete_repo
4. Generate and COPY the token
5. Save it using ONE of these methods:

USB DRIVE (recommended):
  Create a file on any USB drive:
  → PersonalAccessToken.txt
  Paste your token as the only content.
  GithubTool scans drives D:-Z: automatically.

ENVIRONMENT VARIABLE:
  Set GITHUB_TOKEN=ghp_your_token_here
  (System Properties → Environment Variables)

Then click [Refresh] or restart the app!
        """)
        
        # What's New in v2.0.2
        self._add_section(content, "🆕 What's New in v2.0.2", """
NEW IN v2.0.2 - SMART ACTIONS UPDATE! 🎯

RIGHT PANEL OVERHAUL:
• ⭐ Actions tab: Open, Clone, ZIP, Star
• 🔧 Manage tab: Toggle Privacy, Fork, Rename
• ���️ Danger tab: Delete Repository
• Same space, more features (icon-only tabs!)

NEW TOOLBAR BUTTONS:
• 🔑 Token: Check status or set up new token
  - No token? Opens GitHub token page
  - Has token? Shows info in console
• 📊 Stats: Dumps tab statistics to console
  - Repo counts, privacy breakdown
  - Stars, forks, issues totals
  - Top languages, largest repo
  - ALL output to console (no popups!)

NEW MANAGE ACTIONS:
• 🔒 Toggle Privacy: Public ↔ Private
• 🔀 Fork Repo: Fork to your account
• ✏️ Rename Repo: Change repo name on GitHub
• All confirmations via dialog, results via console

PREVIOUS VERSIONS:
v2.0.1: Push to Branch, ZIP download fix, Delete repo
v2.0.0: Safety checks, prevent overwrites, rollback
        """)
        
        # Creation Lab Guide
        self._add_section(content, "⚡ Using Creation Lab (SAFE!)", """
TAB 5: CREATION LAB WORKFLOW

STEP 1: Repository Details
• Enter repo name (required)
• Add description (optional)
• Choose parent folder location

STEPS 2 & 3: Side-by-Side (SPACE-EFFICIENT!)
LEFT SIDE - README Template:
• ☑ Generate README.md
• Choose template: Basic, Detailed, or Minimal
• Preview before creating

RIGHT SIDE - LICENSE (Optional):
• ☑ Add LICENSE file
• Choose: MIT, GPL-3.0, Apache-2.0, BSD-3-Clause
• Preview license text

STEP 4: Git & GitHub
• ☑ Initialize Git (runs git init)
• ☑ Publish to GitHub (requires token)
  - Choose Private or Public
  - ✅ NOW WITH SAFETY CHECKS!

SAFETY FEATURES (NEW IN v2.0.0):
• Checks if repo exists on GitHub
• Shows warning if name is taken
• Prevents accidental overwrites
• Clear, safe options

BUTTONS:
[Create Local Repo] - Always safe (checks local)
[Publish to GitHub] - Now checks remote first!
        """)
        
        # Star Feature Guide
                # Right Panel Guide
        self._add_section(content, "⭐ Right Panel Actions", """
RIGHT PANEL - THREE TABBED SECTIONS:

[⭐] QUICK ACTIONS:
• 🌐 Open in Browser
• 📥 Clone Selected
• 📦 Download ZIP
• ☆ Star / ⭐ Unstar Repo

[🔧] MANAGE REPO:
• 🔒 Toggle Privacy (Public ↔ Private)
• 🔀 Fork Repo (copy to your account)
• ✏️ Rename Repo (changes GitHub URL!)

[⚠️] DANGER ZONE:
• 🗑️ Delete Repository (2 confirmations!)

All results report to the Diagnostics Console.
No popup spam - check console for details!
        """)
        
        # Features Section
         # Features Section
        self._add_section(content, "✨ Key Features", """
TOOLBAR:
• [Refresh] - Reload all data
• [🔑 Token] - Token status/setup
• [📊 Stats] - Dump tab stats to console
• [Export] CSV/TXT - Export repo lists
• [Search] + [Filter] - Find repos fast

RIGHT PANEL (Tabbed):
• Rate limit monitor
• Repository details
• [⭐] Actions: Open, Clone, ZIP, Star
• [🔧] Manage: Privacy, Fork, Rename
• [⚠️] Danger: Delete

TABS 0-5:
• Tab 0: Welcome (this page)
• Tab 1: My Repos / Public Browse
• Tab 2: Organization Repos
• Tab 3: Starred Repos
• Tab 4: Download From Others
• Tab 5: Creation Lab (create + publish)

CONSOLE-FIRST DESIGN (v2.0.2):
• Stats → console
• Token info → console
• Privacy toggle → console
• Fork results → console
• Rename results → console
• No unnecessary popup windows!

TAB 1-3: My Repos, Org Repos, Starred
• Repository tables with sorting
• Export to CSV/TXT
• Search and filter

TAB 4: Download From Others
• Tree view for browsing repos
• README viewer (tall and clear)
• Repository properties
• Release assets

TAB 5: Creation Lab ⚡ (SAFE & SPACE-EFFICIENT!)
• Create local repositories
• Generate README templates
• Add LICENSE files
• Publish to GitHub with SAFETY CHECKS 🛡️
• Side-by-side layout saves space

SAFETY FEATURES (v2.0.0!):
• Pre-publish checks
• Prevents overwrites
• Clear warnings and options

DIAGNOSTICS CONSOLE:
• Resizable! Drag the divider ↕️
• Stays visible with compact layout
• Timestamped logs
        """)
        
        # Bottom separator
        separator2 = ttk.Separator(content, orient="horizontal")
        separator2.pack(fill="x", padx=40, pady=20)
        
        # Footer
        footer = ttk.Label(content, text="v2.0.2 - Console is King! 🎯", 
                          font=("TkDefaultFont", 12, "italic"))
        footer.pack(pady=(10, 30))
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _add_section(self, parent, title: str, content: str):
        """Add a content section with title and text."""
        frame = ttk.LabelFrame(parent, text=title, padding=10)
        frame.pack(fill="x", padx=20, pady=10)
        
        text = tk.Text(frame, wrap="word", height=content.count('\n') + 1, 
                      relief="flat", bg='white', font=("Courier", 9))
        text.insert("1.0", content.strip())
        text.configure(state="disabled")
        text.pack(fill="x")


# ============================================================================
# MODULE: CreationLabTab (ENHANCED IN v2.0.0 - SAFETY CHECKS!)
# Description: Tab for creating local repos with templates and GitHub publishing
# Drop: Added in Drop 3.6
#       Enhanced in Drop 3.7: Steps 2 & 3 side-by-side for space efficiency
#       Enhanced in v2.0.0: Safety checks before publishing (prevent overwrites)
# ============================================================================
class CreationLabTab(ttk.Frame):
    """
    Tab for creating local repositories with README/LICENSE templates
    and optional GitHub publishing.
    
    Added in: Drop 3.6
    Enhanced in: Drop 3.7 - Steps 2 & 3 side-by-side to save vertical space
    Enhanced in: v2.0.0 - Safety checks to prevent overwriting existing repos
    """
    
    def __init__(self, master, diag_append: Callable[[str], None]):
        super().__init__(master)
        self.diag_append = diag_append
        
        # ------------------------------------------------------------------------
        # SECTION: Main Content Area (Left)
        # ------------------------------------------------------------------------
        content = ttk.Frame(self)
        content.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        
        # Step 1: Repository Details
        step1 = ttk.LabelFrame(content, text="Step 1: Repository Details", padding=10)
        step1.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(step1, text="Repository Name (required):").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(step1, width=40)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        ttk.Label(step1, text="Description (optional):").grid(row=1, column=0, sticky="w", pady=5)
        self.desc_entry = ttk.Entry(step1, width=40)
        self.desc_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        ttk.Label(step1, text="Parent Folder:").grid(row=2, column=0, sticky="w", pady=5)
        location_frame = ttk.Frame(step1)
        location_frame.grid(row=2, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        self.location_var = tk.StringVar(value=str(Path.home()))
        self.location_entry = ttk.Entry(location_frame, textvariable=self.location_var, width=30)
        self.location_entry.pack(side="left", fill="x", expand=True)
        
        browse_btn = ttk.Button(location_frame, text="Browse...", command=self.browse_location)
        browse_btn.pack(side="left", padx=(5, 0))
        
        step1.grid_columnconfigure(1, weight=1)
        
        # Steps 2 & 3 + Center Branding - THREE COLUMNS
        steps_frame = ttk.Frame(content)
        steps_frame.pack(fill="x", padx=10, pady=5)
        
        steps_frame.grid_columnconfigure(0, weight=3)  # Step 2 (30%)
        steps_frame.grid_columnconfigure(1, weight=4)  # Center branding (40%)
        steps_frame.grid_columnconfigure(2, weight=3)  # Step 3 (30%)
        
                # ---- LEFT: Step 2 - README ----
        step2 = ttk.LabelFrame(steps_frame, text="Step 2: README", padding=8)
        step2.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.readme_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(step2, text="Generate README.md", 
                        variable=self.readme_var).pack(anchor="w", pady=(0, 3))
        
        ttk.Label(step2, text="Template:").pack(anchor="w", pady=(2, 2))
        self.template_var = tk.StringVar(value="Basic")
        ttk.Combobox(step2, textvariable=self.template_var,
                     values=list(README_TEMPLATES.keys()),
                     state="readonly", width=14).pack(anchor="w", pady=(0, 3))
        
        ttk.Button(step2, text="Preview", 
                   command=self.preview_readme).pack(anchor="w", pady=(2, 0))
                   
         # ---- CENTER: Branding Block (Lightning Bolt Graphic) ----
        center = ttk.LabelFrame(steps_frame, text="🧪 Creation Lab", padding=8)
        center.grid(row=0, column=1, sticky="nsew", padx=5)
        
        center_inner = ttk.Frame(center)
        center_inner.pack(expand=True)
        
        ttk.Label(center_inner, text="⚡", 
                  font=("Segoe UI Emoji", 30)).pack(pady=(5, 3))
        ttk.Label(center_inner, text="GitHubTool Creation Lab", 
                  font=("Segoe UI", 14, "bold")).pack()
        ttk.Label(center_inner, text="v2.0.2     © kindle15", 
                  font=("Segoe UI", 8), foreground="gray").pack(pady=(3, 0))
                  
        # ---- RIGHT: Step 3 - LICENSE ----
        step3 = ttk.LabelFrame(steps_frame, text="Step 3: LICENSE", padding=8)
        step3.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        
        self.license_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(step3, text="Add LICENSE file", 
                        variable=self.license_var).pack(anchor="w", pady=(0, 3))
        
        ttk.Label(step3, text="Type:").pack(anchor="w", pady=(2, 2))
        self.license_type_var = tk.StringVar(value="MIT")
        ttk.Combobox(step3, textvariable=self.license_type_var,
                     values=list(LICENSE_TEMPLATES.keys()),
                     state="readonly", width=14).pack(anchor="w", pady=(0, 3))
        
        ttk.Button(step3, text="Preview", 
                   command=self.preview_license).pack(anchor="w", pady=(2, 0))

                   
        # ------------------------------------------------------------------------
        # SECTION: Step 4 + Push to Branch - SIDE BY SIDE
        # ------------------------------------------------------------------------
        step4_row = ttk.Frame(content)
        step4_row.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Configure columns: 40% Step 4, 60% Push to Branch
        step4_row.grid_columnconfigure(0, weight=2)
        step4_row.grid_columnconfigure(1, weight=3)
        
        # ---- LEFT SIDE: Step 4 - Git & GitHub ----
        step4 = ttk.LabelFrame(step4_row, text="Step 4: Git & GitHub", padding=10)
        step4.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.git_init_var = tk.BooleanVar(value=True)
        git_check = ttk.Checkbutton(step4, text="Initialize Git (git init)", variable=self.git_init_var)
        git_check.pack(anchor="w", pady=(0, 5))
        
        self.publish_var = tk.BooleanVar(value=False)
        publish_check = ttk.Checkbutton(step4, text="Publish to GitHub", 
                                        variable=self.publish_var,
                                        command=self.toggle_publish_options)
        publish_check.pack(anchor="w", pady=(0, 5))
        
        privacy_frame = ttk.Frame(step4)
        privacy_frame.pack(anchor="w", padx=(20, 0), pady=(0, 5))
        
        self.private_var = tk.BooleanVar(value=True)
        ttk.Label(privacy_frame, text="Privacy:").pack(side="left", padx=(0, 5))
        ttk.Radiobutton(privacy_frame, text="Private", variable=self.private_var, 
                       value=True).pack(side="left", padx=(0, 10))
        ttk.Radiobutton(privacy_frame, text="Public", variable=self.private_var, 
                       value=False).pack(side="left")
        
        # Buttons inside Step 4
        step4_btns = ttk.Frame(step4)
        step4_btns.pack(anchor="w", pady=(10, 0))
        
        self.create_btn = ttk.Button(step4_btns, text="Create Local Repo", 
                                     command=self.create_local_async)
        self.create_btn.pack(side="left", padx=(0, 5))
        
        self.publish_btn = ttk.Button(step4_btns, text="Publish to GitHub", 
                                      command=self.publish_to_github_async,
                                      state="disabled")
        self.publish_btn.pack(side="left")
        
            # ---- RIGHT SIDE: Push to Branch (COMPACT GRID) ----
        push_frame = ttk.LabelFrame(step4_row, text="Push to Branch (Existing Repos)", padding=8)
        push_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Configure grid: labels col 0, entries col 1, browse col 2
        push_frame.grid_columnconfigure(1, weight=1)
        
        # Row 0: Local Folder
        ttk.Label(push_frame, text="Folder:").grid(row=0, column=0, sticky="w", pady=3, padx=(0, 5))
        self.push_folder_var = tk.StringVar(value="")
        self.push_folder_entry = ttk.Entry(push_frame, textvariable=self.push_folder_var)
        self.push_folder_entry.grid(row=0, column=1, sticky="ew", pady=3)
        push_browse_btn = ttk.Button(push_frame, text="...", width=3,
                                     command=self._push_browse_folder)
        push_browse_btn.grid(row=0, column=2, sticky="w", pady=3, padx=(3, 0))
        
        # Row 1: Target Repo
        ttk.Label(push_frame, text="Repo:").grid(row=1, column=0, sticky="w", pady=3, padx=(0, 5))
        self.push_repo_var = tk.StringVar(value="")
        self.push_repo_entry = ttk.Entry(push_frame, textvariable=self.push_repo_var)
        self.push_repo_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=3)
        
        # Row 2: Branch Name
        ttk.Label(push_frame, text="Branch:").grid(row=2, column=0, sticky="w", pady=3, padx=(0, 5))
        self.push_branch_var = tk.StringVar(value="main")
        self.push_branch_entry = ttk.Entry(push_frame, textvariable=self.push_branch_var)
        self.push_branch_entry.grid(row=2, column=1, columnspan=2, sticky="ew", pady=3)
        
        # Row 3: Commit Message
        ttk.Label(push_frame, text="Message:").grid(row=3, column=0, sticky="w", pady=3, padx=(0, 5))
        self.push_message_var = tk.StringVar(value="")
        self.push_message_entry = ttk.Entry(push_frame, textvariable=self.push_message_var)
        self.push_message_entry.grid(row=3, column=1, columnspan=2, sticky="ew", pady=3)
        
        # Row 4: Buttons
        push_btns = ttk.Frame(push_frame)
        push_btns.grid(row=4, column=0, columnspan=3, sticky="w", pady=(6, 0))
        
        self.check_push_btn = ttk.Button(push_btns, text="🔍 Check Status", 
                                         command=self._check_push_status_async)
        self.check_push_btn.pack(side="left", padx=(0, 5))
        
        self.push_branch_btn = ttk.Button(push_btns, text="⬆️ Push to Branch", 
                                          command=self._push_to_branch_async)
        self.push_branch_btn.pack(side="left", padx=(0, 5))
        
        self.publish_existing_btn = ttk.Button(push_btns, text="🚀 Publish Folder", 
                                               command=self._publish_existing_folder_async)
        self.publish_existing_btn.pack(side="left")
        
        # State
        self.last_created_path: Optional[Path] = None
        
    def _append_diag(self, text: str) -> None:
        """Alias for diag_append (convenience method)."""
        self.diag_append(text)
    
    def browse_location(self) -> None:
        """Open folder picker for parent directory."""
        folder = filedialog.askdirectory(title="Select Parent Folder", 
                                        initialdir=self.location_var.get())
        if folder:
            self.location_var.set(folder)
    
    def toggle_publish_options(self) -> None:
        """Enable/disable publish-related options based on checkbox."""
        pass
    
    def preview_readme(self) -> None:
        """Preview the selected README template in diagnostics."""
        template_name = self.template_var.get()
        template = README_TEMPLATES.get(template_name, "")
        
        repo_name = self.name_entry.get().strip() or "{REPO_NAME}"
        description = self.desc_entry.get().strip() or "{DESCRIPTION}"
        
        preview = template.replace("{REPO_NAME}", repo_name).replace("{DESCRIPTION}", description)
        
        self.diag_append("=" * 50)
        self.diag_append(f"README Preview ({template_name} Template):")
        self.diag_append("=" * 50)
        for line in preview.split('\n'):
            self.diag_append(line)
        self.diag_append("=" * 50)
    
    def preview_license(self) -> None:
        """Preview the selected LICENSE template in diagnostics."""
        license_type = self.license_type_var.get()
        template = LICENSE_TEMPLATES.get(license_type, "")
        
        year = datetime.now().year
        author = "Your Name"
        
        preview = template.replace("{YEAR}", str(year)).replace("{AUTHOR}", author)
        
        self.diag_append("=" * 50)
        self.diag_append(f"LICENSE Preview ({license_type}):")
        self.diag_append("=" * 50)
        for line in preview.split('\n')[:20]:
            self.diag_append(line)
        self.diag_append("... (truncated)")
        self.diag_append("=" * 50)
    
    def create_local_async(self) -> None:
        """Create local repository asynchronously."""
        threading.Thread(target=self.create_local_repo, daemon=True).start()
    
    def create_local_repo(self) -> None:
        """Create local repository with selected options."""
        # Validate input
        repo_name = self.name_entry.get().strip()
        if not repo_name:
            messagebox.showerror("Error", "Repository name is required!")
            return
        
        description = self.desc_entry.get().strip()
        parent_folder = Path(self.location_var.get())
        
        if not parent_folder.exists():
            messagebox.showerror("Error", f"Parent folder does not exist: {parent_folder}")
            return
        
        repo_path = parent_folder / repo_name
        
        # Check if already exists
        if repo_path.exists():
            messagebox.showerror("Error", f"Folder already exists: {repo_path}")
            return
        
        try:
            self.diag_append(f"Creating repository: {repo_name}")
            self.diag_append(f"Location: {repo_path}")
            
            # Create folder
            repo_path.mkdir(parents=True, exist_ok=False)
            self.diag_append(f"✓ Created folder: {repo_path}")
            
            # Generate README
            if self.readme_var.get():
                template_name = self.template_var.get()
                template = README_TEMPLATES.get(template_name, README_TEMPLATES["Basic"])
                readme_content = template.replace("{REPO_NAME}", repo_name).replace("{DESCRIPTION}", description)
                
                readme_path = repo_path / "README.md"
                readme_path.write_text(readme_content, encoding='utf-8')
                self.diag_append(f"✓ Generated README.md ({template_name} template)")
            
            # Generate LICENSE
            if self.license_var.get():
                license_type = self.license_type_var.get()
                template = LICENSE_TEMPLATES.get(license_type, LICENSE_TEMPLATES["MIT"])
                year = datetime.now().year
                author = "Your Name"
                
                license_content = template.replace("{YEAR}", str(year)).replace("{AUTHOR}", author)
                
                license_path = repo_path / "LICENSE"
                license_path.write_text(license_content, encoding='utf-8')
                self.diag_append(f"✓ Generated LICENSE ({license_type})")
            
            # Initialize Git
            if self.git_init_var.get():
                result = subprocess.run(
                    ["git", "init"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.diag_append("✓ Initialized Git repository")
                    
                    # Add initial commit
                    add_result = subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True, text=True)
                    
                    # Check if there are files to commit
                    status_result = subprocess.run(
                        ["git", "status", "--porcelain"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True
                    )
                    
                    if status_result.stdout.strip():
                        # There are staged files - commit them
                        commit_result = subprocess.run(
                            ["git", "commit", "-m", "Initial commit"],
                            cwd=repo_path,
                            capture_output=True,
                            text=True
                        )
                        if commit_result.returncode == 0:
                            self.diag_append("✓ Created initial commit")
                        else:
                            self.diag_append(f"⚠ Commit failed: {commit_result.stderr.strip()}")
                    else:
                        # No files to commit - create a placeholder .gitkeep
                        self.diag_append("⚠ No files to commit - creating .gitkeep placeholder")
                        gitkeep_path = repo_path / ".gitkeep"
                        gitkeep_path.write_text("", encoding='utf-8')
                        subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True)
                        commit_result = subprocess.run(
                            ["git", "commit", "-m", "Initial commit"],
                            cwd=repo_path,
                            capture_output=True,
                            text=True
                        )
                        if commit_result.returncode == 0:
                            self.diag_append("✓ Created initial commit (with .gitkeep)")
                        else:
                            self.diag_append(f"⚠ Commit failed: {commit_result.stderr.strip()}")
                else:
                    self.diag_append(f"⚠ Git init failed: {result.stderr}")
            
            self.diag_append(f"✅ Repository created successfully!")
            self.diag_append(f"📂 Path: {repo_path}")
            
            # Store path for publishing
            self.last_created_path = repo_path
            
            # Enable publish button if publish option was checked
            if self.publish_var.get():
                self.publish_btn.config(state="normal")
            
            messagebox.showinfo("Success", f"Repository created successfully!\n\nPath: {repo_path}")
            
        except Exception as e:
            self.diag_append(f"❌ Failed to create repository: {e}")
            messagebox.showerror("Error", f"Failed to create repository:\n{e}")
    
    def publish_to_github_async(self) -> None:
        """Publish repository to GitHub asynchronously."""
        threading.Thread(target=self.publish_to_github, daemon=True).start()
    
    def publish_to_github(self) -> None:
        """
        Publish the local repository to GitHub.
        
        Enhanced in v2.0.0: 
        - Safety checks before creating
        - Automatic rollback if push fails
        - Strips .git extension from names
        """
        if not self.last_created_path or not self.last_created_path.exists():
            messagebox.showerror("Error", "No local repository to publish!\n\nCreate a local repo first.")
            return
        
        try:
            # Get token
            token, source = get_token()
            
            if not token:
                messagebox.showerror(
                    "GitHub Token Required",
                    f"Publishing to GitHub requires authentication.\n\nToken status: {source}\n\n"
                    "Please ensure your token is available via:\n"
                    "• Flash drive with token file\n"
                    "• Environment variable: GITHUB_TOKEN\n"
                    "• Config file: ~/.github_token"
                )
                return
            
            # Get repo name and strip .git extension if present (FIX #5)
            repo_name = self.last_created_path.name
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
                self.diag_append(f"ℹ️ Stripped .git extension from repo name: {repo_name}")
            
            description = self.desc_entry.get().strip()
            is_private = self.private_var.get()
            
            # ==================================================================
            # STEP 1: SAFETY CHECK - Does repo already exist on GitHub?
            # ==================================================================
            self.diag_append(f"🔍 STEP 1: Checking if {repo_name} already exists on GitHub...")
            
            try:
                username = get_authenticated_user(token)
                exists, existing_repo = check_if_repo_exists(username, repo_name, token)
                
                if exists:
                    self.diag_append(f"⚠️ Repository {username}/{repo_name} already exists on GitHub!")
                    self.diag_append(f"❌ Publishing CANCELLED - repo exists")
                    self._show_repo_exists_dialog(existing_repo, username, repo_name)
                    return
                else:
                    self.diag_append(f"✅ Repository name '{repo_name}' is available")
            except Exception as e:
                self.diag_append(f"⚠️ Could not verify if repo exists: {e}")
                proceed = messagebox.askyesno(
                    "Cannot Verify",
                    f"Could not verify if repository exists:\n{e}\n\nContinue anyway?\n\n"
                    f"WARNING: If the repo exists, this will fail!"
                )
                if not proceed:
                    self.diag_append(f"❌ Publishing CANCELLED by user")
                    return
            
            # ==================================================================
            # STEP 2: CREATE REPO ON GITHUB
            # ==================================================================
            self.diag_append(f"📤 STEP 2: Creating repository '{repo_name}' on GitHub...")
            self.diag_append(f"   Privacy: {'Private' if is_private else 'Public'}")
            
            try:
                repo_data = create_github_repository(repo_name, description, is_private, token)
                clone_url = repo_data.get("clone_url", "")
                html_url = repo_data.get("html_url", "")
                
                self.diag_append(f"✅ Repository created on GitHub: {html_url}")
            except Exception as e:
                if "already exists" in str(e).lower() or "name already exists" in str(e).lower():
                    self.diag_append(f"❌ FAILED: Repository '{username}/{repo_name}' already exists!")
                    messagebox.showerror(
                        "Repository Exists",
                        f"Repository '{username}/{repo_name}' already exists on GitHub!\n\n{e}"
                    )
                else:
                    self.diag_append(f"❌ Failed to create repository: {e}")
                    messagebox.showerror("Creation Failed", f"Failed to create repository:\n\n{e}")
                return
            
            # ==================================================================
            # STEP 3: ADD REMOTE (WITH ROLLBACK ON FAILURE)
            # ==================================================================
            self.diag_append(f"🔗 STEP 3: Configuring git remote...")
            
            try:
                # Check if 'origin' remote exists
                check_remote = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=self.last_created_path,
                    capture_output=True,
                    text=True
                )
                
                if check_remote.returncode == 0:
                    # Remote exists - update it
                    existing_url = check_remote.stdout.strip()
                    self.diag_append(f"ℹ️ Remote 'origin' exists: {existing_url}")
                    
                    if existing_url != clone_url:
                        self.diag_append(f"🔄 Updating remote URL to: {clone_url}")
                        subprocess.run(
                            ["git", "remote", "set-url", "origin", clone_url],
                            cwd=self.last_created_path,
                            capture_output=True,
                            text=True
                        )
                        self.diag_append(f"✅ Remote URL updated")
                    else:
                        self.diag_append(f"✅ Remote URL is correct")
                else:
                    # Add remote
                    self.diag_append(f"➕ Adding remote 'origin': {clone_url}")
                    result = subprocess.run(
                        ["git", "remote", "add", "origin", clone_url],
                        cwd=self.last_created_path,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        raise Exception(f"Failed to add remote: {result.stderr}")
                    
                    self.diag_append(f"✅ Remote 'origin' added")
            
            except Exception as e:
                # Remote setup failed - ROLLBACK!
                self.diag_append(f"❌ Remote setup failed: {e}")
                self.diag_append(f"🔄 Rolling back: Deleting repo from GitHub...")
                
                if self._delete_github_repo(username, repo_name, token):
                    self.diag_append(f"✅ Rollback complete: GitHub repo deleted")
                    messagebox.showerror(
                        "Remote Setup Failed",
                        f"Failed to configure git remote:\n{e}\n\n"
                        f"The empty repository on GitHub has been automatically deleted.\n"
                        f"Please try again."
                    )
                else:
                    self.diag_append(f"⚠️ Rollback failed: Could not delete repo")
                    messagebox.showerror(
                        "Remote Setup Failed",
                        f"Failed to configure git remote:\n{e}\n\n"
                        f"An empty repository was created on GitHub but couldn't be deleted.\n"
                        f"Please manually delete: {html_url}"
                    )
                return
            
            # ==================================================================
            # STEP 4: PUSH TO GITHUB (WITH ROLLBACK ON FAILURE)
            # ==================================================================
            self.diag_append(f"⬆️ STEP 4: Pushing to GitHub...")
            
            #             # Detect actual branch name instead of guessing
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.last_created_path,
                capture_output=True,
                text=True
            )
            
            if branch_result.returncode == 0 and branch_result.stdout.strip():
                branch_name = branch_result.stdout.strip()
                self.diag_append(f"🌿 Detected branch: {branch_name}")
            else:
                # Fallback: try to detect from git branch output
                branch_list = subprocess.run(
                    ["git", "branch"],
                    cwd=self.last_created_path,
                    capture_output=True,
                    text=True
                )
                if branch_list.stdout.strip():
                    # Parse "* main" or "* master" from output
                    for line in branch_list.stdout.strip().split('\n'):
                        if line.startswith('*'):
                            branch_name = line.replace('*', '').strip()
                            break
                    else:
                        branch_name = "main"
                else:
                    branch_name = "main"
                self.diag_append(f"🌿 Using branch: {branch_name}")
            
            result = subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                cwd=self.last_created_path,
                capture_output=True,
                text=True
            )
            
            # Check if push succeeded
            if result.returncode == 0:
                self.diag_append(f"✅ Successfully pushed to GitHub")
                self.diag_append(f"=" * 60)
                self.diag_append(f"🎉 PUBLICATION COMPLETE!")
                self.diag_append(f"🌐 URL: {html_url}")
                self.diag_append(f"=" * 60)
                
                messagebox.showinfo(
                    "🎉 Success!",
                    f"Repository published to GitHub!\n\n"
                    f"📦 Repository: {username}/{repo_name}\n"
                    f"🔒 Privacy: {'Private' if is_private else 'Public'}\n"
                    f"🌐 URL: {html_url}\n\n"
                    f"Click OK to open in browser."
                )
                webbrowser.open(html_url)
            else:
                # Push failed - ROLLBACK!
                error_msg = result.stderr.strip()
                self.diag_append(f"❌ Push failed: {error_msg}")
                self.diag_append(f"🔄 Rolling back: Deleting repo from GitHub...")
                
                if self._delete_github_repo(username, repo_name, token):
                    self.diag_append(f"✅ Rollback complete: GitHub repo deleted")
                    messagebox.showerror(
                        "Push Failed",
                        f"Failed to push to GitHub:\n{error_msg}\n\n"
                        f"The empty repository on GitHub has been automatically deleted.\n\n"
                        f"Common fixes:\n"
                        f"• Ensure you have commits in your local repo\n"
                        f"• Check your internet connection\n"
                        f"• Verify your token has write permissions"
                    )
                else:
                    self.diag_append(f"⚠️ Rollback failed: Could not delete repo")
                    messagebox.showerror(
                        "Push Failed",
                        f"Failed to push to GitHub:\n{error_msg}\n\n"
                        f"An empty repository was created but couldn't be deleted.\n"
                        f"Please manually delete: {html_url}"
                    )
        
        except Exception as e:
            self.diag_append(f"=" * 60)
            self.diag_append(f"❌ PUBLICATION FAILED")
            self.diag_append(f"Error: {e}")
            self.diag_append(f"=" * 60)
            messagebox.showerror("Error", f"Failed to publish to GitHub:\n\n{e}")
    
        # ========================================================================
    # SECTION: Push to Branch Methods (Added in v2.0.1)
    # ========================================================================
    def _push_browse_folder(self) -> None:
        """Browse for local folder to push."""
        folder = filedialog.askdirectory(
            title="Select Local Repository Folder",
            initialdir=self.push_folder_var.get() or str(Path.home())
        )
        if folder:
            self.push_folder_var.set(folder)
    
    def _check_push_status_async(self) -> None:
        """Check push status asynchronously."""
        threading.Thread(target=self._check_push_status, daemon=True).start()
    
    def _check_push_status(self) -> None:
        """
        Check all prerequisites for pushing to a branch.
        
        Checks:
        1. Local folder is a git repository
        2. Target repo exists on GitHub
        3. Branch exists on remote
        4. Shows summary of changes
        """
        self.diag_append("=" * 60)
        self.diag_append("🔍 PUSH CHECK: Starting pre-push validation...")
        self.diag_append("=" * 60)
        
        # Validate inputs
        folder = self.push_folder_var.get().strip()
        target_repo = self.push_repo_var.get().strip()
        branch = self.push_branch_var.get().strip()
        
        if not folder:
            self.diag_append("❌ Check FAILED: No local folder specified")
            messagebox.showwarning("Check Failed", "Please specify a local folder.")
            return
        
        if not target_repo:
            self.diag_append("❌ Check FAILED: No target repo specified")
            messagebox.showwarning("Check Failed", "Please specify a target repo (owner/repo).")
            return
        
        if '/' not in target_repo:
            self.diag_append("❌ Check FAILED: Target repo must be in owner/repo format")
            messagebox.showwarning("Check Failed", "Target repo must be in owner/repo format.\nExample: kindle15/test4")
            return
        
        if not branch:
            self.diag_append("❌ Check FAILED: No branch name specified")
            messagebox.showwarning("Check Failed", "Please specify a branch name.")
            return
        
        folder_path = Path(folder)
        all_ok = True
        
        # ==================================================================
        # CHECK 1: Does folder exist?
        # ==================================================================
        self.diag_append(f"📂 Local folder: {folder}")
        
        if not folder_path.exists():
            self.diag_append(f"❌ Check 1 FAILED: Folder does not exist")
            messagebox.showerror("Check Failed", f"Folder does not exist:\n{folder}")
            return
        
        self.diag_append(f"✅ Folder exists")
        
        # ==================================================================
        # CHECK 2: Is it a git repository?
        # ==================================================================
        git_dir = folder_path / ".git"
        if not git_dir.exists():
            self.diag_append(f"❌ Check 2 FAILED: Not a git repository (no .git folder)")
            self.diag_append(f"💡 Use Step 4 to create a new repository with git init")
            messagebox.showerror(
                "Not a Git Repository",
                f"This folder is not a git repository:\n{folder}\n\n"
                f"No .git folder found.\n\n"
                f"Use Step 4 (Create Local Repo) with 'Initialize Git' checked,\n"
                f"or run 'git init' in the folder first."
            )
            return
        
        self.diag_append(f"✅ Git initialized (.git folder found)")
        
        # ==================================================================
        # CHECK 3: Does target repo exist on GitHub?
        # ==================================================================
        self.diag_append(f"🔗 Target repo: {target_repo}")
        
        try:
            token, _ = get_token()
            if not token:
                self.diag_append(f"❌ Check 3 FAILED: No GitHub token available")
                messagebox.showerror(
                    "Authentication Required",
                    "Pushing to GitHub requires a token.\n\n"
                    "Please ensure your token is available."
                )
                return
            
            parts = target_repo.split('/')
            owner = parts[0]
            repo_name = parts[1]
            
            exists, repo_data = check_if_repo_exists(owner, repo_name, token)
            
            if not exists:
                self.diag_append(f"❌ Check 3 FAILED: Repository {target_repo} does NOT exist on GitHub!")
                self.diag_append(f"💡 Use Step 4 to create the repository first")
                messagebox.showerror(
                    "Repository Not Found",
                    f"Repository {target_repo} does not exist on GitHub!\n\n"
                    f"Use Step 4 (Create Local Repo + Publish to GitHub)\n"
                    f"to create it first."
                )
                return
            
            self.diag_append(f"✅ Repository exists on GitHub")
            
            # Show repo info
            repo_private = "Private" if repo_data.get("private", False) else "Public"
            repo_default_branch = repo_data.get("default_branch", "main")
            self.diag_append(f"   Privacy: {repo_private}")
            self.diag_append(f"   Default branch: {repo_default_branch}")
        
        except Exception as e:
            self.diag_append(f"⚠️ Check 3 WARNING: Could not verify repo: {e}")
            all_ok = False
        
        # ==================================================================
        # CHECK 4: Does branch exist on remote?
        # ==================================================================
        self.diag_append(f"🌿 Branch: {branch}")
        
        try:
            branch_url = f"https://api.github.com/repos/{target_repo}/branches/{branch}"
            headers = {
                "User-Agent": "GithubTool/2.0.2",
                "Authorization": f"token {token}"
            }
            
            req = urllib.request.Request(branch_url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    self.diag_append(f"✅ Branch '{branch}' exists on remote")
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    self.diag_append(f"⚠️ Branch '{branch}' does NOT exist on remote")
                    self.diag_append(f"💡 It will be created when you push")
                    all_ok = True  # This is OK - will be created on push
                else:
                    self.diag_append(f"⚠️ Could not check branch: HTTP {e.code}")
                    all_ok = False
        except Exception as e:
            self.diag_append(f"⚠️ Could not check branch: {e}")
            all_ok = False
        
        # ==================================================================
        # CHECK 5: Git status summary
        # ==================================================================
        try:
            # Check for uncommitted changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=folder_path,
                capture_output=True,
                text=True
            )
            
            if status_result.returncode == 0:
                status_lines = [l for l in status_result.stdout.strip().split('\n') if l.strip()]
                
                if status_lines:
                    modified = sum(1 for l in status_lines if l.startswith(' M') or l.startswith('M '))
                    added = sum(1 for l in status_lines if l.startswith('??') or l.startswith('A '))
                    deleted = sum(1 for l in status_lines if l.startswith(' D') or l.startswith('D '))
                    other = len(status_lines) - modified - added - deleted
                    
                    self.diag_append(f"📊 Working directory changes:")
                    self.diag_append(f"   Modified: {modified}")
                    self.diag_append(f"   New/Untracked: {added}")
                    self.diag_append(f"   Deleted: {deleted}")
                    if other > 0:
                        self.diag_append(f"   Other: {other}")
                    self.diag_append(f"   Total changes: {len(status_lines)}")
                else:
                    self.diag_append(f"📊 Working directory: Clean (no changes)")
            
            # Check current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=folder_path,
                capture_output=True,
                text=True
            )
            
            if branch_result.returncode == 0 and branch_result.stdout.strip():
                current_branch = branch_result.stdout.strip()
                self.diag_append(f"🌿 Current local branch: {current_branch}")
                
                if current_branch != branch:
                    self.diag_append(f"ℹ️ Will switch from '{current_branch}' to '{branch}'")
            
            # Check remote
            remote_result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=folder_path,
                capture_output=True,
                text=True
            )
            
            if remote_result.returncode == 0 and remote_result.stdout.strip():
                self.diag_append(f"🔗 Existing remotes:")
                for line in remote_result.stdout.strip().split('\n'):
                    self.diag_append(f"   {line}")
            else:
                self.diag_append(f"ℹ️ No remotes configured (will add 'origin')")
        
        except Exception as e:
            self.diag_append(f"⚠️ Could not get git status: {e}")
        
        # ==================================================================
        # FINAL SUMMARY
        # ==================================================================
        self.diag_append("=" * 60)
        if all_ok:
            self.diag_append("✅ PRE-PUSH CHECK COMPLETE - Ready to push!")
        else:
            self.diag_append("⚠️ PRE-PUSH CHECK COMPLETE - Some warnings (see above)")
        self.diag_append("=" * 60)
    
    def _push_to_branch_async(self) -> None:
        """Push to branch - validation on main thread, push on background thread."""
        # Validate inputs on MAIN THREAD
        folder = self.push_folder_var.get().strip()
        target_repo = self.push_repo_var.get().strip()
        branch = self.push_branch_var.get().strip()
        message = self.push_message_var.get().strip()
        
        if not folder:
            messagebox.showwarning("Push", "Please specify a local folder.")
            return
        
        if not target_repo:
            messagebox.showwarning("Push", "Please specify a target repo (owner/repo).")
            return
        
        if '/' not in target_repo:
            messagebox.showwarning("Push", "Target repo must be in owner/repo format.\nExample: kindle15/test4")
            return
        
        if not branch:
            messagebox.showwarning("Push", "Please specify a branch name.")
            return
        
        if not message:
            messagebox.showwarning("Push", "Please enter a commit message.")
            return
        
        folder_path = Path(folder)
        
        if not folder_path.exists():
            messagebox.showerror("Push", f"Folder does not exist:\n{folder}")
            return
        
        if not (folder_path / ".git").exists():
            self.diag_append(f"❌ Push FAILED: {folder} is not a git repository")
            self.diag_append(f"💡 Use Step 4 to create a new repository first")
            messagebox.showerror(
                "Not a Git Repository",
                f"This folder is not a git repository:\n{folder}\n\n"
                f"Use Step 4 to create a repository with git init."
            )
            return
        
        # Confirm push
        confirm = messagebox.askyesno(
            "Confirm Push",
            f"Push to GitHub?\n\n"
            f"📂 From: {folder}\n"
            f"📦 To: {target_repo}\n"
            f"🌿 Branch: {branch}\n"
            f"💬 Message: {message}\n\n"
            f"Continue?"
        )
        
        if not confirm:
            self.diag_append("⬆️ Push cancelled by user")
            return
        
        # Do push on BACKGROUND THREAD
        threading.Thread(
            target=self._do_push_to_branch,
            args=(folder_path, target_repo, branch, message),
            daemon=True
        ).start()
    
    def _do_push_to_branch(self, folder_path: Path, target_repo: str, branch: str, message: str) -> None:
        """
        Execute the push to branch operation.
        
        Steps:
        1. Verify repo exists on GitHub
        2. Configure remote
        3. Stage changes
        4. Commit
        5. Switch/create branch
        6. Push
        """
        self.diag_append("=" * 60)
        self.diag_append("⬆️ PUSH TO BRANCH: Starting...")
        self.diag_append("=" * 60)
        
        try:
            # Get token
            token, source = get_token()
            if not token:
                self.diag_append("❌ Push FAILED: No GitHub token")
                messagebox.showerror("Authentication Required", "Pushing requires a GitHub token.")
                return
            
            parts = target_repo.split('/')
            owner = parts[0]
            repo_name = parts[1]
            
            # ==================================================================
            # STEP 1: Verify repo exists on GitHub
            # ==================================================================
            self.diag_append(f"🔍 Step 1: Verifying {target_repo} exists on GitHub...")
            
            try:
                exists, repo_data = check_if_repo_exists(owner, repo_name, token)
                
                if not exists:
                    self.diag_append(f"❌ Repository {target_repo} does NOT exist on GitHub!")
                    self.diag_append(f"💡 Use Step 4 to create the repository first")
                    messagebox.showerror(
                        "Repository Not Found",
                        f"Repository {target_repo} does not exist!\n\n"
                        f"Use Step 4 (Create Local Repo + Publish)\n"
                        f"to create it first."
                    )
                    return
                
                self.diag_append(f"✅ Repository exists")
                clone_url = repo_data.get("clone_url", f"https://github.com/{target_repo}.git")
                html_url = repo_data.get("html_url", f"https://github.com/{target_repo}")
            
            except Exception as e:
                self.diag_append(f"⚠️ Could not verify repo: {e}")
                proceed = messagebox.askyesno(
                    "Cannot Verify",
                    f"Could not verify repository exists:\n{e}\n\n"
                    f"Continue anyway?"
                )
                if not proceed:
                    self.diag_append("❌ Push cancelled by user")
                    return
                clone_url = f"https://github.com/{target_repo}.git"
                html_url = f"https://github.com/{target_repo}"
            
            # ==================================================================
            # STEP 2: Configure remote
            # ==================================================================
            self.diag_append(f"🔗 Step 2: Configuring remote...")
            
            # Check if 'origin' exists
            check_remote = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=folder_path,
                capture_output=True,
                text=True
            )
            
            if check_remote.returncode == 0:
                existing_url = check_remote.stdout.strip()
                expected_url = clone_url
                
                if existing_url != expected_url:
                    self.diag_append(f"🔄 Updating remote 'origin': {existing_url} → {expected_url}")
                    subprocess.run(
                        ["git", "remote", "set-url", "origin", expected_url],
                        cwd=folder_path,
                        capture_output=True,
                        text=True
                    )
                else:
                    self.diag_append(f"✅ Remote 'origin' already set to: {existing_url}")
            else:
                self.diag_append(f"➕ Adding remote 'origin': {clone_url}")
                result = subprocess.run(
                    ["git", "remote", "add", "origin", clone_url],
                    cwd=folder_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    self.diag_append(f"❌ Failed to add remote: {result.stderr}")
                    messagebox.showerror("Remote Failed", f"Failed to add remote:\n{result.stderr}")
                    return
            
            self.diag_append(f"✅ Remote configured")
            
            # ==================================================================
            # STEP 3: Stage all changes
            # ==================================================================
            self.diag_append(f"📋 Step 3: Staging changes...")
            
            add_result = subprocess.run(
                ["git", "add", "."],
                cwd=folder_path,
                capture_output=True,
                text=True
            )
            
            if add_result.returncode != 0:
                self.diag_append(f"❌ git add failed: {add_result.stderr}")
                messagebox.showerror("Stage Failed", f"Failed to stage files:\n{add_result.stderr}")
                return
            
            self.diag_append(f"✅ Changes staged")
            
            # ==================================================================
            # STEP 4: Commit
            # ==================================================================
            self.diag_append(f"💬 Step 4: Committing: {message}")
            
            commit_result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=folder_path,
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode != 0:
                stderr = commit_result.stderr.strip()
                stdout = commit_result.stdout.strip()
                
                # "nothing to commit" is not an error
                if "nothing to commit" in stdout or "nothing to commit" in stderr:
                    self.diag_append(f"ℹ️ Nothing to commit (working tree clean)")
                    self.diag_append(f"ℹ️ Proceeding to push existing commits...")
                else:
                    self.diag_append(f"❌ Commit failed: {stderr or stdout}")
                    messagebox.showerror("Commit Failed", f"Failed to commit:\n{stderr or stdout}")
                    return
            else:
                self.diag_append(f"✅ Committed")
            
            # ==================================================================
            # STEP 5: Switch/create branch
            # ==================================================================
            self.diag_append(f"🌿 Step 5: Switching to branch '{branch}'...")
            
            # Check current branch
            current_branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=folder_path,
                capture_output=True,
                text=True
            )
            current_branch = current_branch_result.stdout.strip() if current_branch_result.returncode == 0 else ""
            
            if current_branch == branch:
                self.diag_append(f"✅ Already on branch '{branch}'")
            else:
                # Try to checkout existing branch
                checkout_result = subprocess.run(
                    ["git", "checkout", branch],
                    cwd=folder_path,
                    capture_output=True,
                    text=True
                )
                
                if checkout_result.returncode != 0:
                    # Branch doesn't exist locally - check if user wants to create it
                    self.diag_append(f"ℹ️ Branch '{branch}' doesn't exist locally")
                    
                    # Check if it exists on remote
                    try:
                        branch_url = f"https://api.github.com/repos/{target_repo}/branches/{branch}"
                        headers = {
                            "User-Agent": "GithubTool/2.0.2",
                            "Authorization": f"token {token}"
                        }
                        req = urllib.request.Request(branch_url, headers=headers)
                        try:
                            with urllib.request.urlopen(req, timeout=10):
                                # Branch exists on remote - checkout tracking branch
                                self.diag_append(f"🌿 Branch exists on remote, checking out...")
                                fetch_result = subprocess.run(
                                    ["git", "fetch", "origin", branch],
                                    cwd=folder_path,
                                    capture_output=True,
                                    text=True
                                )
                                checkout_result = subprocess.run(
                                    ["git", "checkout", "-b", branch, f"origin/{branch}"],
                                    cwd=folder_path,
                                    capture_output=True,
                                    text=True
                                )
                                if checkout_result.returncode != 0:
                                    # Try simpler checkout
                                    checkout_result = subprocess.run(
                                        ["git", "checkout", "-b", branch],
                                        cwd=folder_path,
                                        capture_output=True,
                                        text=True
                                    )
                        except urllib.error.HTTPError as e:
                            if e.code == 404:
                                # Branch doesn't exist anywhere - ask to create
                                create_branch = messagebox.askyesno(
                                    "Branch Not Found",
                                    f"Branch '{branch}' does not exist.\n\n"
                                    f"Create it as a new branch?"
                                )
                                if not create_branch:
                                    self.diag_append(f"❌ Push cancelled - user declined branch creation")
                                    return
                                
                                checkout_result = subprocess.run(
                                    ["git", "checkout", "-b", branch],
                                    cwd=folder_path,
                                    capture_output=True,
                                    text=True
                                )
                            else:
                                # Can't check - just try to create
                                checkout_result = subprocess.run(
                                    ["git", "checkout", "-b", branch],
                                    cwd=folder_path,
                                    capture_output=True,
                                    text=True
                                )
                    except Exception:
                        # Network error - just try to create branch
                        checkout_result = subprocess.run(
                            ["git", "checkout", "-b", branch],
                            cwd=folder_path,
                            capture_output=True,
                            text=True
                        )
                    
                    if checkout_result.returncode != 0:
                        self.diag_append(f"❌ Failed to switch to branch '{branch}': {checkout_result.stderr}")
                        messagebox.showerror("Branch Failed", f"Could not switch to branch '{branch}':\n{checkout_result.stderr}")
                        return
                
                self.diag_append(f"✅ On branch '{branch}'")
            
            # ==================================================================
            # STEP 6: Push to remote
            # ==================================================================
            self.diag_append(f"⬆️ Step 6: Pushing to origin/{branch}...")
            
            push_result = subprocess.run(
                ["git", "push", "-u", "origin", branch],
                cwd=folder_path,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode == 0:
                branch_url = f"{html_url}/tree/{branch}"
                
                self.diag_append(f"=" * 60)
                self.diag_append(f"✅ PUSH SUCCESSFUL!")
                self.diag_append(f"📦 Repository: {target_repo}")
                self.diag_append(f"🌿 Branch: {branch}")
                self.diag_append(f"💬 Message: {message}")
                self.diag_append(f"🌐 URL: {branch_url}")
                self.diag_append(f"=" * 60)
                
                messagebox.showinfo(
                    "✅ Push Successful!",
                    f"Successfully pushed to GitHub!\n\n"
                    f"📦 Repository: {target_repo}\n"
                    f"🌿 Branch: {branch}\n"
                    f"💬 Message: {message}\n\n"
                    f"🌐 {branch_url}"
                )
            else:
                error_msg = push_result.stderr.strip()
                self.diag_append(f"❌ Push FAILED: {error_msg}")
                
                if "rejected" in error_msg.lower():
                    messagebox.showerror(
                        "Push Rejected",
                        f"Push was rejected by GitHub:\n\n{error_msg}\n\n"
                        f"This usually means the remote has changes you don't have.\n\n"
                        f"Try:\n"
                        f"  git pull origin {branch}\n"
                        f"Then push again."
                    )
                elif "permission" in error_msg.lower() or "denied" in error_msg.lower():
                    messagebox.showerror(
                        "Permission Denied",
                        f"Push was denied:\n\n{error_msg}\n\n"
                        f"Check that your token has write access to {target_repo}."
                    )
                else:
                    messagebox.showerror(
                        "Push Failed",
                        f"Failed to push:\n\n{error_msg}"
                    )
        
        except Exception as e:
            self.diag_append(f"=" * 60)
            self.diag_append(f"❌ PUSH FAILED: {e}")
            self.diag_append(f"=" * 60)
            messagebox.showerror("Push Failed", f"Failed to push:\n\n{e}")
            
    # ========================================================================
    # SECTION: Publish Existing Folder (Added in v2.0.2)
    # ========================================================================
    def _publish_existing_folder_async(self) -> None:
        """Publish an existing local folder to GitHub - validates on main thread, work on background."""
        
        # Get folder from the push_folder field, or ask for one
        folder = self.push_folder_var.get().strip()
        
        if not folder:
            folder = filedialog.askdirectory(
                title="Select Existing Folder to Publish",
                initialdir=str(Path.home())
            )
            if not folder:
                return
            self.push_folder_var.set(folder)
        
        folder_path = Path(folder)
        
        if not folder_path.exists():
            messagebox.showerror("Publish", f"Folder does not exist:\n{folder}")
            return
        
        # Check if folder has any files
        files = [f for f in folder_path.iterdir() if f.name != '.git']
        if not files:
            messagebox.showwarning(
                "Empty Folder",
                f"This folder appears to be empty:\n{folder}\n\n"
                f"Add some files first, then try again."
            )
            return
        
        # Use folder name as repo name, let user confirm/change
        default_name = folder_path.name
        if default_name.endswith('.git'):
            default_name = default_name[:-4]
        
        repo_name = simpledialog.askstring(
            "Repository Name",
            f"Folder: {folder_path.name}\n\n"
            f"Enter the GitHub repository name:",
            initialvalue=default_name
        )
        
        if not repo_name or not repo_name.strip():
            self.diag_append("🚀 Publish Existing: Cancelled — no name entered")
            return
        
        repo_name = repo_name.strip()
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        # Ask privacy
        is_private = messagebox.askyesno(
            "Repository Privacy",
            f"Make '{repo_name}' private?\n\n"
            f"Yes = Private (only you can see it)\n"
            f"No = Public (anyone can see it)"
        )
        
        privacy_label = "Private" if is_private else "Public"
        
        # Final confirmation
        confirm = messagebox.askyesno(
            "Confirm Publish",
            f"Publish existing folder to GitHub?\n\n"
            f"📂 Folder: {folder}\n"
            f"📦 Repo name: {repo_name}\n"
            f"🔒 Privacy: {privacy_label}\n"
            f"📄 Files: {len(files)} items\n\n"
            f"This will:\n"
            f"  1. Initialize git (if needed)\n"
            f"  2. Create repo on GitHub\n"
            f"  3. Commit all files\n"
            f"  4. Push to GitHub\n\n"
            f"Continue?"
        )
        
        if not confirm:
            self.diag_append("🚀 Publish Existing: Cancelled by user")
            return
        
        # Do the work on background thread
        threading.Thread(
            target=self._do_publish_existing_folder,
            args=(folder_path, repo_name, is_private),
            daemon=True
        ).start()
    
    def _do_publish_existing_folder(self, folder_path: Path, repo_name: str, is_private: bool) -> None:
        """
        Execute the full publish-existing-folder workflow.
        
        Handles:
        1. Git init (if not already a repo)
        2. Safety check (repo exists on GitHub?)
        3. Create repo on GitHub
        4. Configure remote
        5. Stage + commit all files
        6. Push
        7. Rollback on failure
        """
        self.diag_append("=" * 60)
        self.diag_append("🚀 PUBLISH EXISTING FOLDER")
        self.diag_append("=" * 60)
        self.diag_append(f"   Folder: {folder_path}")
        self.diag_append(f"   Repo:   {repo_name}")
        self.diag_append(f"   Privacy: {'Private' if is_private else 'Public'}")
        self.diag_append("")
        
        # Get token
        token, source = get_token()
        if not token:
            self.diag_append("❌ No GitHub token available")
            messagebox.showerror("Authentication Required", "Publishing requires a GitHub token.")
            return
        
        try:
            username = get_authenticated_user(token)
            self.diag_append(f"   User:   {username}")
        except Exception as e:
            self.diag_append(f"❌ Could not get username: {e}")
            messagebox.showerror("Auth Error", f"Could not verify authentication:\n{e}")
            return
        
        # ==================================================================
        # STEP 1: Git init (if needed)
        # ==================================================================
        git_dir = folder_path / ".git"
        if git_dir.exists():
            self.diag_append("✅ Step 1: Already a git repository")
            
            # Check if existing repo has problematic history
            # (e.g., previous failed publish with too many files)
            try:
                log_result = subprocess.run(
                    ["git", "count-objects", "-vH"],
                    cwd=folder_path,
                    capture_output=True,
                    text=True
                )
                if log_result.returncode == 0:
                    output = log_result.stdout
                    self.diag_append(f"   Git objects: {output.strip().split(chr(10))[0]}")
                    
                    # Check size-pack for large repos
                    for line in output.split('\n'):
                        if 'size-pack' in line:
                            try:
                                size_str = line.split(':')[1].strip()
                                # Parse size (could be "50.00 MiB" or "500 KiB" or bytes)
                                if 'MiB' in size_str or 'GiB' in size_str:
                                    self.diag_append(f"   ⚠️ Pack size: {size_str}")
                                    
                                    reinit = messagebox.askyesno(
                                        "Large Git History Detected",
                                        f"This folder has a large git history:\n"
                                        f"Pack size: {size_str}\n\n"
                                        f"This may be from a previous failed publish\n"
                                        f"that included too many files.\n\n"
                                        f"Reinitialize git? (Recommended)\n\n"
                                        f"Yes = Delete .git and start fresh\n"
                                        f"No = Keep existing history"
                                    )
                                    
                                    if reinit:
                                        import shutil
                                        shutil.rmtree(git_dir)
                                        self.diag_append("🔄 Removed old .git folder")
                                        
                                        result = subprocess.run(
                                            ["git", "init"],
                                            cwd=folder_path,
                                            capture_output=True,
                                            text=True
                                        )
                                        if result.returncode == 0:
                                            self.diag_append("✅ Git reinitialized (clean slate)")
                                        else:
                                            self.diag_append(f"❌ git init failed: {result.stderr}")
                                            return
                            except Exception:
                                pass
            except Exception as e:
                self.diag_append(f"   ℹ️ Could not check git objects: {e}")
        else:
            self.diag_append("🔧 Step 1: Initializing git...")
            result = subprocess.run(
                ["git", "init"],
                cwd=folder_path,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.diag_append(f"❌ git init failed: {result.stderr.strip()}")
                messagebox.showerror("Git Init Failed", f"Failed to initialize git:\n{result.stderr}")
                return
            self.diag_append("✅ Git initialized")
        
        # ==================================================================
        # STEP 1.5: Ensure .gitignore exists
        # ==================================================================
        gitignore_path = folder_path / ".gitignore"
        if not gitignore_path.exists():
            self.diag_append("📄 Step 1.5: Creating default .gitignore...")
            default_gitignore = """# === GithubTool Default .gitignore ===

# Python virtual environments (catches all naming patterns)
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
*.egg
.eggs/
venv/
.venv/
env/
.env/
*_env/
env_*/
.python-version

# PyInstaller
build/
*.spec.bak

# NOTE: dist/ is NOT excluded — we want built executables uploaded!
# NOTE: *.exe in dist/ will be pushed. Standalone *.exe in root is excluded.

# Node
node_modules/
npm-debug.log*

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.project
.settings/

# OS
.DS_Store
Thumbs.db
desktop.ini
$RECYCLE.BIN/

# Logs
*.log

# Large archives (unlikely to be source code)
# Uncomment if needed:
# *.zip
# *.tar.gz
# *.rar
# *.7z
"""
            gitignore_path.write_text(default_gitignore, encoding='utf-8')
            self.diag_append("✅ Created default .gitignore")
            self.diag_append("   (excludes __pycache__, node_modules, venv, etc.)")
        else:
            self.diag_append("✅ Step 1.5: .gitignore already exists")

        # ==================================================================
        # STEP 2: Safety check — does repo exist on GitHub?
        # ==================================================================
        self.diag_append(f"🔍 Step 2: Checking if {username}/{repo_name} exists on GitHub...")
        
        try:
            exists, existing_repo = check_if_repo_exists(username, repo_name, token)
            
            if exists:
                self.diag_append(f"⚠️ Repository {username}/{repo_name} already exists!")
                
                use_existing = messagebox.askyesno(
                    "Repository Exists",
                    f"Repository {username}/{repo_name} already exists on GitHub!\n\n"
                    f"Would you like to push to the EXISTING repo instead?\n\n"
                    f"Yes = Push to existing repo\n"
                    f"No = Cancel"
                )
                
                if not use_existing:
                    self.diag_append("❌ Cancelled — repo already exists")
                    return
                
                # Use existing repo
                self.diag_append("ℹ️ Using existing repository")
                clone_url = existing_repo.get("clone_url", f"https://github.com/{username}/{repo_name}.git")
                html_url = existing_repo.get("html_url", f"https://github.com/{username}/{repo_name}")
                created_new = False
            else:
                self.diag_append(f"✅ Name '{repo_name}' is available")
                created_new = True
        except Exception as e:
            self.diag_append(f"⚠️ Could not check: {e}")
            proceed = messagebox.askyesno(
                "Cannot Verify",
                f"Could not check if repo exists:\n{e}\n\nContinue anyway?"
            )
            if not proceed:
                return
            created_new = True
        
        # ==================================================================
        # STEP 3: Create repo on GitHub (if new)
        # ==================================================================
        if created_new:
            self.diag_append(f"📤 Step 3: Creating {username}/{repo_name} on GitHub...")
            
            try:
                description = ""  # Could prompt for this later
                repo_data = create_github_repository(repo_name, description, is_private, token)
                clone_url = repo_data.get("clone_url", "")
                html_url = repo_data.get("html_url", "")
                self.diag_append(f"✅ Repository created: {html_url}")
            except Exception as e:
                self.diag_append(f"❌ Failed to create repo: {e}")
                messagebox.showerror("Creation Failed", f"Failed to create repository:\n{e}")
                return
        else:
            self.diag_append(f"⏭️ Step 3: Skipped (using existing repo)")
        
        # ==================================================================
        # STEP 4: Configure remote
        # ==================================================================
        self.diag_append(f"🔗 Step 4: Configuring remote...")
        
        try:
            check_remote = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=folder_path,
                capture_output=True,
                text=True
            )
            
            if check_remote.returncode == 0:
                existing_url = check_remote.stdout.strip()
                if existing_url != clone_url:
                    self.diag_append(f"🔄 Updating remote: {existing_url} → {clone_url}")
                    subprocess.run(
                        ["git", "remote", "set-url", "origin", clone_url],
                        cwd=folder_path,
                        capture_output=True,
                        text=True
                    )
                else:
                    self.diag_append(f"✅ Remote already set correctly")
            else:
                self.diag_append(f"➕ Adding remote 'origin': {clone_url}")
                result = subprocess.run(
                    ["git", "remote", "add", "origin", clone_url],
                    cwd=folder_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    raise Exception(f"Failed to add remote: {result.stderr}")
            
            self.diag_append(f"✅ Remote configured")
        
        except Exception as e:
            self.diag_append(f"❌ Remote setup failed: {e}")
            if created_new:
                self.diag_append("🔄 Rolling back: Deleting repo from GitHub...")
                if self._delete_github_repo(username, repo_name, token):
                    self.diag_append("✅ Rollback complete")
                else:
                    self.diag_append(f"⚠️ Rollback failed — manually delete: {html_url}")
            messagebox.showerror("Remote Failed", f"Failed to configure remote:\n{e}")
            return
        
        # ==================================================================
        # STEP 5: Stage + commit all files
        # ==================================================================
        self.diag_append(f"📋 Step 5: Staging and committing files...")
        
        # Stage everything
        add_result = subprocess.run(
            ["git", "add", "."],
            cwd=folder_path,
            capture_output=True,
            text=True
        )
        
        if add_result.returncode != 0:
            self.diag_append(f"❌ git add failed: {add_result.stderr.strip()}")
            if created_new:
                self.diag_append("🔄 Rolling back...")
                self._delete_github_repo(username, repo_name, token)
            return
        
        # Check if there's anything to commit
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=folder_path,
            capture_output=True,
            text=True
        )
        
        if status_result.stdout.strip():
            file_count = len([l for l in status_result.stdout.strip().split('\n') if l.strip()])
            self.diag_append(f"   {file_count} files staged")
            
            # Warn if too many files (likely missing .gitignore)
            if file_count > 1000:
                self.diag_append(f"⚠️ WARNING: {file_count} files is a lot!")
                self.diag_append(f"   This may include node_modules/, venv/, or build artifacts.")
                self.diag_append(f"   Consider adding a .gitignore file first.")
                
                proceed = messagebox.askyesno(
                    "Large Repository Warning",
                    f"⚠️ {file_count} files staged!\n\n"
                    f"This is unusually large and may include\n"
                    f"files that shouldn't be pushed:\n"
                    f"  • node_modules/\n"
                    f"  • venv/ or .venv/\n"
                    f"  • __pycache__/\n"
                    f"  • build artifacts\n\n"
                    f"A default .gitignore was created (if missing).\n\n"
                    f"Yes = Continue anyway\n"
                    f"No = Cancel (review .gitignore first)"
                )
                
                if not proceed:
                    self.diag_append("❌ Cancelled — too many files")
                    if created_new:
                        self.diag_append("🔄 Rolling back...")
                        self._delete_github_repo(username, repo_name, token)
                    return
            
            commit_result = subprocess.run(
                ["git", "commit", "-m", "Initial commit — published via GithubTool"],
                cwd=folder_path,
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode != 0:
                stderr = commit_result.stderr.strip()
                stdout = commit_result.stdout.strip()
                if "nothing to commit" not in stdout and "nothing to commit" not in stderr:
                    self.diag_append(f"❌ Commit failed: {stderr or stdout}")
                    if created_new:
                        self.diag_append("🔄 Rolling back...")
                        self._delete_github_repo(username, repo_name, token)
                    return
                else:
                    self.diag_append("ℹ️ Nothing new to commit (existing commits will be pushed)")
            else:
                self.diag_append("✅ Files committed")
        else:
            self.diag_append("ℹ️ No changes to commit (pushing existing commits)")
        
        # ==================================================================
        # STEP 6: Detect branch and push
        # ==================================================================
        self.diag_append(f"⬆️ Step 6: Pushing to GitHub...")
        
        # Increase git HTTP buffer for large initial pushes
        subprocess.run(
            ["git", "config", "http.postBuffer", "524288000"],
            cwd=folder_path,
            capture_output=True,
            text=True
        )
        self.diag_append("   Set http.postBuffer to 500MB")

        # Detect actual branch name
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=folder_path,
            capture_output=True,
            text=True
        )
        
        if branch_result.returncode == 0 and branch_result.stdout.strip():
            branch_name = branch_result.stdout.strip()
        else:
            # Fallback: parse git branch output
            branch_list = subprocess.run(
                ["git", "branch"],
                cwd=folder_path,
                capture_output=True,
                text=True
            )
            branch_name = "main"  # default
            if branch_list.stdout.strip():
                for line in branch_list.stdout.strip().split('\n'):
                    if line.startswith('*'):
                        branch_name = line.replace('*', '').strip()
                        break
        
        self.diag_append(f"🌿 Branch: {branch_name}")
        
        push_result = subprocess.run(
            ["git", "push", "-u", "origin", branch_name],
            cwd=folder_path,
            capture_output=True,
            text=True
        )
        
        if push_result.returncode == 0:
            self.diag_append("=" * 60)
            self.diag_append("🎉 PUBLISH SUCCESSFUL!")
            self.diag_append(f"   📦 Repository: {username}/{repo_name}")
            self.diag_append(f"   🌿 Branch: {branch_name}")
            self.diag_append(f"   🔒 Privacy: {'Private' if is_private else 'Public'}")
            self.diag_append(f"   🌐 URL: {html_url}")
            self.diag_append("=" * 60)
            
            messagebox.showinfo(
                "🎉 Published!",
                f"Folder published to GitHub!\n\n"
                f"📦 {username}/{repo_name}\n"
                f"🌿 Branch: {branch_name}\n"
                f"🔒 {'Private' if is_private else 'Public'}\n\n"
                f"🌐 {html_url}"
            )
            webbrowser.open(html_url)
        else:
            error_msg = push_result.stderr.strip()
            self.diag_append(f"❌ Push failed: {error_msg}")
            
            if created_new:
                self.diag_append("🔄 Rolling back: Deleting repo from GitHub...")
                if self._delete_github_repo(username, repo_name, token):
                    self.diag_append("✅ Rollback complete")
                else:
                    self.diag_append(f"⚠️ Rollback failed — manually delete: {html_url}")
            
            if "rejected" in error_msg.lower():
                messagebox.showerror(
                    "Push Rejected",
                    f"Push was rejected:\n\n{error_msg}\n\n"
                    f"The remote has changes you don't have.\n"
                    f"Use 'Push to Branch' with git pull first."
                )
            else:
                messagebox.showerror("Push Failed", f"Failed to push:\n\n{error_msg}")
    
    def _show_repo_exists_dialog(self, existing_repo: Dict, username: str, repo_name: str) -> None:
        """
        Show dialog when repository already exists on GitHub.
        
        Added in: v2.0.0
        """
        # Extract info from existing repo
        html_url = existing_repo.get("html_url", "")
        updated_at = existing_repo.get("updated_at", "Unknown")
        pushed_at = existing_repo.get("pushed_at", "Unknown")
        size = existing_repo.get("size", 0)
        default_branch = existing_repo.get("default_branch", "main")

        # Format dates
        try:
            updated_date = updated_at[:10] if len(updated_at) > 10 else updated_at
            pushed_date = pushed_at[:10] if len(pushed_at) > 10 else pushed_at
        except:
            updated_date = "Unknown"
            pushed_date = "Unknown"
        
        # Create custom dialog
        dialog = tk.Toplevel(self)
        dialog.title("⚠️ Repository Already Exists")
        dialog.geometry("500x350")
        dialog.transient(self)
        dialog.grab_set()
        
        # Content frame
        content = ttk.Frame(dialog, padding=20)
        content.pack(fill="both", expand=True)
        
        # Warning header
        warning_label = ttk.Label(content, text="⚠️ Repository Already Exists on GitHub!", 
                                 font=("TkDefaultFont", 12, "bold"), 
                                 foreground="red")
        warning_label.pack(pady=(0, 15))
        
        # Info text
        info_text = f"""Repository: {username}/{repo_name}
Status: Already exists with content
Last updated: {updated_date}
Last pushed: {pushed_date}
Size: {size} KB
Default branch: {default_branch}

URL: {html_url}

This repository already exists and may contain data.
Publishing now could cause conflicts or data loss.

What would you like to do?"""
        
        info_label = ttk.Label(content, text=info_text, justify="left", 
                              font=("TkDefaultFont", 9))
        info_label.pack(pady=(0, 20))
        
        # Separator
        separator = ttk.Separator(content, orient="horizontal")
        separator.pack(fill="x", pady=(0, 15))
        
        # Button frame
        button_frame = ttk.Frame(content)
        button_frame.pack(fill="x")
        
        def cancel_action():
            self.diag_append("❌ Publishing cancelled - repo already exists")
            dialog.destroy()
        
        def view_on_github():
            self.diag_append(f"🌐 Opening existing repo in browser: {html_url}")
            webbrowser.open(html_url)
            dialog.destroy()
        
        def add_remote_only():
            """Add existing repo as remote without creating new one."""
            try:
                clone_url = existing_repo.get("clone_url", "")
                if not clone_url:
                    messagebox.showerror("Error", "Could not get clone URL")
                    return
                
                # Add remote
                result = subprocess.run(
                    ["git", "remote", "add", "origin", clone_url],
                    cwd=self.last_created_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.diag_append(f"✓ Added existing repo as remote: {clone_url}")
                    messagebox.showinfo(
                        "Remote Added",
                        f"Added existing repository as remote.\n\n"
                        f"You can now manually review and push:\n"
                        f"  git fetch origin\n"
                        f"  git merge origin/{default_branch}\n"
                        f"  git push origin {default_branch}"
                    )
                else:
                    self.diag_append(f"⚠️ Failed to add remote: {result.stderr}")
                    messagebox.showerror("Error", f"Failed to add remote:\n{result.stderr}")
                
                dialog.destroy()
            except Exception as e:
                self.diag_append(f"❌ Failed to add remote: {e}")
                messagebox.showerror("Error", f"Failed to add remote:\n{e}")
        
        # Buttons
        ttk.Button(button_frame, text="��� Cancel (Safest)", 
                  command=cancel_action).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="🔗 Add as Remote Only", 
                  command=add_remote_only).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="🌐 View on GitHub", 
                  command=view_on_github).pack(side="left", padx=5)
# ================================================================================
#FIX 6 : Delete Github Repo Helper
# ================================================================================

    def _delete_github_repo(self, owner: str, repo_name: str, token: str) -> bool:
        """
        Delete a repository from GitHub.
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            token: GitHub API token
        
        Returns:
            True if deleted successfully, False otherwise
        
        Added in: v2.0.0 (for rollback functionality)
        """
        try:
            url = f"https://api.github.com/repos/{owner}/{repo_name}"
            headers = {
                "User-Agent": "GithubTool/2.0.2",
                "Authorization": f"token {token}"
            }
            
            req = urllib.request.Request(url, headers=headers, method='DELETE')
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 204  # 204 = successfully deleted
        except Exception as e:
            self.diag_append(f"⚠️ Failed to delete repo: {e}")
            return False

# ============================================================================
# MODULE: ExternalDownloadTab
# Description: Tab for downloading repos from other users with README viewer
# Drop: Added in Drop 1, Enhanced in Drop 2 (README viewer, enhanced properties)
#       Enhanced in Drop 2.1 (export support)
#       Enhanced in Drop 3 (rate limit display) - REMOVED in Drop 3.5
#       Enhanced in Drop 3.5 (Removed old rate limit, uses main right panel now)
# ============================================================================
class ExternalDownloadTab(ttk.Frame):
    """
    Tab that allows downloading repos and release assets from other users.
    Supports owner/repo, owner/, and owner formats.
    
    Enhanced in Drop 2: README viewer, enhanced properties
    Enhanced in Drop 2.1: Export support
    Enhanced in Drop 3: Rate limit display in right panel
    Enhanced in Drop 3.5: Removed duplicate rate limit, unified with main right panel
    """

    def __init__(
        self,
        master,
        diag_append: Callable[[str], None],
        token_getter: Callable[[], Tuple[Optional[str], str]],
        progress_setter: Optional[Callable[[int, int, str], None]] = None,
        progress_clearer: Optional[Callable[[], None]] = None,
    ):
        super().__init__(master)
        self.diag_append = diag_append
        self.token_getter = token_getter
        self.progress_set = progress_setter or (lambda total, done, msg: None)
        self.progress_clear = progress_clearer or (lambda: None)

        # ------------------------------------------------------------------------
        # SECTION: Top Controls
        # ------------------------------------------------------------------------
        top = ttk.Frame(self)
        top.pack(fill="x", padx=6, pady=6)

        ttk.Label(top, text="Owner/Repo or Owner (comma separated)").grid(row=0, column=0, sticky="w")
        self.repo_entry = ttk.Entry(top, width=60)
        self.repo_entry.grid(row=0, column=1, sticky="w", padx=(6, 4))
        self.repo_entry.insert(0, "octocat/Hello-World")

        self.fetch_btn = ttk.Button(top, text="Fetch", command=self.fetch_async)
        self.fetch_btn.grid(row=0, column=2, padx=4)

        # ------------------------------------------------------------------------
        # SECTION: Main Body (3-panel layout)
        # ------------------------------------------------------------------------
        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        left_frame = ttk.Frame(body)
        center_frame = ttk.Frame(body)
        right_frame = ttk.Frame(body)
        
        body.add(left_frame, weight=1)
        body.add(center_frame, weight=2)
        body.add(right_frame, weight=1)

        # Left panel: Repository tree
        self.left_tree = ttk.Treeview(left_frame, columns=("type", "id"), show="tree")
        self.left_tree.pack(fill="both", expand=True, side="left")
        left_scroll = ttk.Scrollbar(left_frame, orient="vertical", command=self.left_tree.yview)
        left_scroll.pack(side="right", fill="y")
        self.left_tree.configure(yscrollcommand=left_scroll.set)
        self.left_tree.bind("<<TreeviewSelect>>", self.on_left_select)

        # ------------------------------------------------------------------------
        # SECTION: Center Panel - README Viewer
        # ------------------------------------------------------------------------
        readme_box = ttk.LabelFrame(center_frame, text="README")
        readme_box.pack(fill="both", expand=True, padx=4, pady=4)

        self.readme_text = tk.Text(readme_box, wrap="word", font=("Courier", 9))
        readme_scroll = ttk.Scrollbar(readme_box, orient="vertical", command=self.readme_text.yview)
        self.readme_text.configure(yscrollcommand=readme_scroll.set)
        self.readme_text.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        readme_scroll.pack(side="right", fill="y")
        self.readme_text.insert("1.0", "Select a repository to view its README")
        self.readme_text.configure(state="disabled")

        # ------------------------------------------------------------------------
        # SECTION: Right Panel - Properties + Assets
        # ------------------------------------------------------------------------
        
        # Properties section
        details_box = ttk.LabelFrame(right_frame, text="Repository Properties")
        details_box.pack(fill="both", expand=True, padx=4, pady=4)

        self.details_text = tk.Text(details_box, wrap="word", font=("Courier", 9))
        details_scroll = ttk.Scrollbar(details_box, orient="vertical", command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scroll.set)
        self.details_text.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        details_scroll.pack(side="right", fill="y")
        self.details_text.configure(state="disabled")

        # Release assets section
        assets_box = ttk.LabelFrame(right_frame, text="Release Assets")
        assets_box.pack(fill="both", expand=True, padx=4, pady=4)

        self.assets_list = ttk.Treeview(assets_box, columns=("name", "size", "download_url"), show="headings", selectmode="extended")
        self.assets_list.heading("name", text="Name")
        self.assets_list.heading("size", text="Size")
        self.assets_list.heading("download_url", text="URL")
        self.assets_list.column("download_url", width=0, stretch=False)
        self.assets_list.pack(fill="both", expand=True, side="left")
        assets_scroll = ttk.Scrollbar(assets_box, orient="vertical", command=self.assets_list.yview)
        assets_scroll.pack(side="right", fill="y")
        self.assets_list.configure(yscrollcommand=assets_scroll.set)

        # ------------------------------------------------------------------------
        # SECTION: Bottom Action Buttons
        # ------------------------------------------------------------------------
        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=6, pady=(0, 6))

        self.download_asset_btn = ttk.Button(btns, text="Download Selected Asset(s)", command=self.download_assets_async)
        self.download_asset_btn.grid(row=0, column=0, padx=4)

        self.download_source_btn = ttk.Button(btns, text="Download Source Zip", command=self.download_source_async)
        self.download_source_btn.grid(row=0, column=1, padx=4)

        self.clone_btn = ttk.Button(btns, text="Clone Repo", command=self.clone_repo_async)
        self.clone_btn.grid(row=0, column=2, padx=4)

        # State variables
        self.repo_map: Dict[str, Any] = {}
        self.current_repo: Optional[Dict] = None
        self.current_release: Optional[Dict] = None
        self.last_populated_repo: Optional[str] = None

    # ------------------------------------------------------------------------
    # SECTION: Helper Methods
    # ------------------------------------------------------------------------
    def _append_diag(self, text: str) -> None:
        """Append message to diagnostics log."""
        try:
            self.diag_append(text)
        except Exception:
            pass

    def _http_get_json(self, url: str, token: Optional[str] = None, timeout: int = 10):
        """Make HTTP GET request and return JSON data."""
        headers = {"User-Agent": "GithubTool/2.0.2"}
        if token:
            headers["Authorization"] = f"token {token}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
            hdrs = {k: v for k, v in resp.getheaders()}
            return data, hdrs

    # ------------------------------------------------------------------------
    # SECTION: Fetch Methods (abbreviated for space - same as Drop 3.7)
    # ------------------------------------------------------------------------
    def fetch_async(self) -> None:
        threading.Thread(target=self.fetch_repos, daemon=True).start()

    def fetch_repos(self) -> None:
        text = self.repo_entry.get().strip()
        if not text:
            self._append_diag("No owner/repo provided")
            return
        entries = [e.strip() for e in text.split(",") if e.strip()]
        token, src = self.token_getter()
        self._append_diag(f"Fetching metadata for {len(entries)} entry/entries using token source: {src}")
        self.left_tree.delete(*self.left_tree.get_children())
        self.repo_map.clear()
        for repo_spec in entries:
            if repo_spec.endswith("/"):
                repo_spec = repo_spec[:-1]
            if "/" not in repo_spec:
                owner = repo_spec
                if not owner:
                    self._append_diag(f"Invalid owner spec: '{repo_spec}'")
                    continue
                try:
                    self._fetch_and_populate_owner_repos(owner, token)
                except Exception as e:
                    self._append_diag(f"Failed to fetch repos for owner {owner}: {e}")
            else:
                try:
                    repo_url = f"https://api.github.com/repos/{repo_spec}"
                    repo_data, _ = self._http_get_json(repo_url, token)
                    repo_item = self.left_tree.insert("", "end", text=repo_spec)
                    self.repo_map[repo_item] = ("repo", repo_data)
                    rels = []
                    page = 1
                    while True:
                        rel_url = f"https://api.github.com/repos/{repo_spec}/releases?per_page=100&page={page}"
                        data, hdrs = self._http_get_json(rel_url, token)
                        if not isinstance(data, list):
                            break
                        rels.extend(data)
                        link = hdrs.get("Link", "")
                        if 'rel="next"' not in link:
                            break
                        page += 1
                    if rels:
                        for r in rels:
                            label = r.get("name") or r.get("tag_name") or f"release {r.get('id')}"
                            child = self.left_tree.insert(repo_item, "end", text=label)
                            self.repo_map[child] = ("release", r, repo_data)
                    else:
                        child = self.left_tree.insert(repo_item, "end", text="(no releases)")
                        self.repo_map[child] = ("noreleases", None, repo_data)
                    self._append_diag(f"Fetched repo {repo_spec} with {len(rels)} releases")
                except Exception as e:
                    self._append_diag(f"Failed to fetch {repo_spec}: {e}")
    
    def _fetch_and_populate_owner_repos(self, owner: str, token: Optional[str]) -> None:
        repos = []
        page = 1
        user_worked = False
        while True:
            url = f"https://api.github.com/users/{owner}/repos?per_page=100&page={page}&sort=updated"
            try:
                data, hdrs = self._http_get_json(url, token)
                if isinstance(data, list):
                    repos.extend(data)
                    user_worked = True
                    link = hdrs.get("Link", "")
                    if 'rel="next"' not in link:
                        break
                    page += 1
                else:
                    break
            except Exception as e:
                self._append_diag(f"User endpoint failed for {owner}: {e}")
                break
        if not user_worked:
            page = 1
            while True:
                url = f"https://api.github.com/orgs/{owner}/repos?per_page=100&page={page}&sort=updated"
                try:
                    data, hdrs = self._http_get_json(url, token)
                    if isinstance(data, list):
                        repos.extend(data)
                        link = hdrs.get("Link", "")
                        if 'rel="next"' not in link:
                            break
                        page += 1
                    else:
                        break
                except Exception as e:
                    self._append_diag(f"Org endpoint failed for {owner}: {e}")
                    break
        if not repos:
            self._append_diag(f"No repos found for owner: {owner}")
            return
        owner_item = self.left_tree.insert("", "end", text=f"{owner}/ ({len(repos)} repos)")
        self.repo_map[owner_item] = ("owner", owner, repos)
        for r in repos:
            name = r.get("name") or r.get("full_name") or "<unknown>"
            child = self.left_tree.insert(owner_item, "end", text=name)
            self.repo_map[child] = ("repo_from_list", r)
        self._append_diag(f"Listed {len(repos)} public repos for owner: {owner}")

    # ------------------------------------------------------------------------
    # SECTION: README & Display Methods (abbreviated - same as Drop 3.7)
    # ------------------------------------------------------------------------
    def _fetch_readme(self, repo: Dict) -> None:
        full_name = repo.get("full_name")
        if not full_name:
            self._set_readme_text("Error: Repository full name not available")
            return
        self._set_readme_text("Loading README...")
        def fetch_thread():
            try:
                token, _ = self.token_getter()
                readme_url = f"https://api.github.com/repos/{full_name}/readme"
                headers = {"User-Agent": "GithubTool/2.0.2"}
                if token:
                    headers["Authorization"] = f"token {token}"
                req = urllib.request.Request(readme_url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    import base64
                    content = data.get("content", "")
                    if content:
                        decoded = base64.b64decode(content).decode("utf-8", errors="replace")
                        self._set_readme_text(decoded)
                        self._append_diag(f"Loaded README for {full_name}")
                    else:
                        self._set_readme_text("README is empty")
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    self._set_readme_text("No README found for this repository")
                    self._append_diag(f"No README found for {full_name}")
                else:
                    self._set_readme_text(f"Error loading README: HTTP {e.code}")
                    self._append_diag(f"Failed to load README for {full_name}: HTTP {e.code}")
            except Exception as e:
                self._set_readme_text(f"Error loading README: {str(e)}")
                self._append_diag(f"Failed to load README for {full_name}: {e}")
        threading.Thread(target=fetch_thread, daemon=True).start()
    
    def _set_readme_text(self, text: str) -> None:
        self.readme_text.configure(state="normal")
        self.readme_text.delete("1.0", "end")
        self.readme_text.insert("end", text)
        self.readme_text.configure(state="disabled")

    def on_left_select(self, event) -> None:
        sel = self.left_tree.selection()
        if not sel:
            return
        item = sel[0]
        info = self.repo_map.get(item)
        if not info:
            return
        kind = info[0]
        if kind == "repo":
            repo = info[1]
            self.current_repo = repo
            self.current_release = None
            self._show_repo_details_enhanced(repo)
            self._fetch_readme(repo)
            self._clear_assets()
        elif kind == "repo_from_list":
            repo = info[1]
            self.current_repo = repo
            self.current_release = None
            self._show_repo_details_enhanced(repo)
            self._fetch_readme(repo)
            self._clear_assets()
            full_name = repo.get("full_name")
            if full_name:
                if self.last_populated_repo != full_name:
                    self.repo_entry.delete(0, "end")
                    self.repo_entry.insert(0, full_name)
                    self._append_diag(f"Populated entry field with: {full_name} (click Fetch to load releases)")
                    self.last_populated_repo = full_name
        elif kind == "owner":
            owner = info[1]
            repos = info[2]
            summary = f"Owner: {owner}\nTotal public repos: {len(repos)}\n\nClick a repository below to view details."
            self.details_text.configure(state="normal")
            self.details_text.delete("1.0", "end")
            self.details_text.insert("end", summary)
            self.details_text.configure(state="disabled")
            self._set_readme_text("Select a repository to view its README")
            self.current_repo = None
            self.current_release = None
            self._clear_assets()
            self.last_populated_repo = None
        elif kind == "release":
            release = info[1]
            repo = info[2]
            self.current_repo = repo
            self.current_release = release
            self._show_release_details(repo, release)
            self._fetch_readme(repo)
            self._populate_assets(release)
        elif kind == "noreleases":
            repo = info[2]
            self.current_repo = repo
            self.current_release = None
            self._show_repo_details_enhanced(repo)
            self._fetch_readme(repo)
            self._clear_assets()

    def _show_repo_details_enhanced(self, repo: Dict) -> None:
        full_name = repo.get('full_name', 'Unknown')
        description = repo.get('description') or 'No description'
        lines = [f"Repository: {full_name}", f"Description: {description}", "", "=" * 50, ""]
        owned_status = "Cloned (Fork)" if repo.get('fork', False) else "Owned (Original)"
        privacy = "Private" if repo.get('private', False) else "Public"
        lines.append(f"Status: {owned_status}")
        lines.append(f"Privacy: {privacy}")
        lines.append("")
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)
        watchers = repo.get('watchers_count', 0)
        open_issues = repo.get('open_issues_count', 0)
        lines.append("Statistics:")
        lines.append(f"  ⭐ Stars: {stars:,}")
        lines.append(f"  🔱 Forks: {forks:,}")
        lines.append(f"  👁️  Watchers: {watchers:,}")
        lines.append(f"  ⚠️  Open Issues: {open_issues:,}")
        lines.append("")
        language = repo.get('language') or 'Not specified'
        default_branch = repo.get('default_branch', 'main')
        license_info = repo.get('license')
        license_name = license_info.get('name') if license_info else 'None'
        lines.append("Technical:")
        lines.append(f"  Language: {language}")
        lines.append(f"  Default Branch: {default_branch}")
        lines.append(f"  License: {license_name}")
        lines.append("")
        created = repo.get('created_at', 'Unknown')
        updated = repo.get('updated_at', 'Unknown')
        pushed = repo.get('pushed_at', 'Unknown')
        lines.append("Timeline:")
        lines.append(f"  Created: {created[:10] if len(created) > 10 else created}")
        lines.append(f"  Updated: {updated[:10] if len(updated) > 10 else updated}")
        lines.append(f"  Last Push: {pushed[:10] if len(pushed) > 10 else pushed}")
        lines.append("")
        html_url = repo.get('html_url', '')
        lines.append(f"URL: {html_url}")
        text = "\n".join(lines)
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("end", text)
        self.details_text.configure(state="disabled")

    def _show_release_details(self, repo: Dict, release: Dict) -> None:
        text = (f"Repo: {repo.get('full_name')}\nRelease: {release.get('name') or release.get('tag_name')}\n"
                f"Tag: {release.get('tag_name')}\nPublished at: {release.get('published_at')}\n\n"
                f"Body:\n{release.get('body') or ''}")
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("end", text)
        self.details_text.configure(state="disabled")

    def _clear_assets(self) -> None:
        for i in self.assets_list.get_children():
            self.assets_list.delete(i)

    def _populate_assets(self, release: Dict) -> None:
        self._clear_assets()
        assets = release.get("assets", []) or []
        for a in assets:
            size = a.get("size", 0)
            name = a.get("name", "")
            url = a.get("browser_download_url") or a.get("url")
            self.assets_list.insert("", "end", values=(name, f"{size} bytes", url))

    def get_current_repo(self) -> Optional[Dict]:
        return self.current_repo

    def get_all_repos_for_export(self) -> List[Dict]:
        repos: List[Dict] = []
        seen_ids: set = set()
        for item_id, info in self.repo_map.items():
            kind = info[0]
            if kind == "repo":
                repo = info[1]
                repo_id = repo.get("id")
                if repo_id and repo_id not in seen_ids:
                    repos.append(repo)
                    seen_ids.add(repo_id)
            elif kind == "repo_from_list":
                repo = info[1]
                repo_id = repo.get("id")
                if repo_id and repo_id not in seen_ids:
                    repos.append(repo)
                    seen_ids.add(repo_id)
            elif kind == "owner":
                owner_repos = info[2]
                for repo in owner_repos:
                    repo_id = repo.get("id")
                    if repo_id and repo_id not in seen_ids:
                        repos.append(repo)
                        seen_ids.add(repo_id)
            elif kind == "release":
                repo = info[2]
                repo_id = repo.get("id")
                if repo_id and repo_id not in seen_ids:
                    repos.append(repo)
                    seen_ids.add(repo_id)
            elif kind == "noreleases":
                repo = info[2]
                repo_id = repo.get("id")
                if repo_id and repo_id not in seen_ids:
                    repos.append(repo)
                    seen_ids.add(repo_id)
        return repos

    # ------------------------------------------------------------------------
    # SECTION: Download Methods (abbreviated - same implementation)
    # ------------------------------------------------------------------------
    def download_assets_async(self) -> None:
        threading.Thread(target=self.download_assets, daemon=True).start()

    def download_assets(self) -> None:
        sel = self.assets_list.selection()
        if not sel:
            self._append_diag("No assets selected")
            messagebox.showwarning("Download", "No assets selected.")
            return
        out_dir = filedialog.askdirectory(title="Select folder to save assets")
        if not out_dir:
            return
        for item in sel:
            vals = self.assets_list.item(item, "values")
            name = vals[0]
            url = vals[2]
            out_path = os.path.join(out_dir, name)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "GithubTool/2.0.2"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    with open(out_path, "wb") as fh:
                        fh.write(resp.read())
                self._append_diag(f"Downloaded {name}")
            except Exception as e:
                self._append_diag(f"Failed: {name}: {e}")
        messagebox.showinfo("Download Complete", "Assets downloaded.")

    def download_source_async(self) -> None:
        threading.Thread(target=self.download_source, daemon=True).start()

    def download_source(self) -> None:
        if not self.current_repo:
            messagebox.showwarning("Download Source", "No repository selected.")
            return
        full_name = self.current_repo.get("full_name")
        branch = simpledialog.askstring("Source Archive", "Branch (blank for default):")
        if branch is None:
            return
        if not branch:
            branch = self.current_repo.get("default_branch") or "main"
        zip_url = f"https://github.com/{full_name}/archive/refs/heads/{branch}.zip"
        out_dir = filedialog.askdirectory(title="Select folder")
        if not out_dir:
            return
        out_path = os.path.join(out_dir, f"{full_name.replace('/', '_')}_{branch}.zip")
        try:
            req = urllib.request.Request(zip_url, headers={'User-Agent': 'GithubTool/2.0.2'})
            with urllib.request.urlopen(req, timeout=60) as resp:
                with open(out_path, 'wb') as fh:
                    fh.write(resp.read())
            messagebox.showinfo("Complete", f"Downloaded to:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Failed", str(e))

    def clone_repo_async(self) -> None:
        threading.Thread(target=self.clone_repo, daemon=True).start()

    def clone_repo(self) -> None:
        if not self.current_repo:
            messagebox.showwarning("Clone", "No repository selected.")
            return
        dest = filedialog.askdirectory(title="Select destination")
        if not dest:
            return
        url = self.current_repo.get("html_url")
        name = self.current_repo.get("name")
        try:
            cmd = ["git", "clone", "--depth", "1", url, os.path.join(dest, name)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                messagebox.showerror("Failed", proc.stderr)
            else:
                messagebox.showinfo("Complete", "Clone finished.")
        except Exception as e:
            messagebox.showerror("Failed", str(e))

# ============================================================================
# MODULE: Main Application (App)
# Description: Main application window and orchestration
# Drop: Added in Drop 1, Enhanced in Drop 2 (Export UI and methods)
#       Enhanced in Drop 2.1 (Tab 4 export support)
#       Enhanced in Drop 3 (Star/Unstar repos functionality)
#       Enhanced in Drop 3.1 (Resizable diagnostics panel)
#       Enhanced in Drop 3.2 (Attempted pack layout fix)
#       Enhanced in Drop 3.3 (GRID LAYOUT - FORCE RIGHT PANEL VISIBLE)
#       Enhanced in Drop 3.4 (FIXED initialization order)
#       Enhanced in Drop 3.5 (UNIFIED LAYOUT - right panel on all tabs, removed Tab 4 duplicate)
#       Enhanced in Drop 3.6 (Added Tab 5 "Creation Lab" for local repo creation & GitHub publish)
#       Enhanced in Drop 3.7 (Space-efficient Creation Lab - Steps 2 & 3 side-by-side)
#       Enhanced in v2.0.0 (Safety checks before publishing + Copyright in About dialog)
# ============================================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # ------------------------------------------------------------------------
        # SECTION: Configuration & Window Setup
        # ------------------------------------------------------------------------
        self.cfg = ConfigManager()
        
        self.title(APP_TITLE)
        geom = self.cfg.get("window_geometry", "1200x700")
        self.geometry(geom)
        self.minsize(900, 500)

        # Set application icon (from embedded icon file)
        try:
            import sys
            import os
    
            # Try to import icon path from app_ico.py
            try:
                from app_ico import ICON_PATH
                self.iconbitmap(default=ICON_PATH)
            except ImportError:
                # Fallback: try to find app.ico in same directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                icon_path = os.path.join(script_dir, "app.ico")
                if os.path.exists(icon_path):
                    self.iconbitmap(icon_path)
        except Exception as e:
            # Icon loading failed - not critical, continue with default
            print(f"Note: Using default icon ({e})")
        #------------------------------------------------------------------------
        # SECTION: Menu Bar
        # ------------------------------------------------------------------------
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Configure Public Browse User", command=self.show_settings_dialog)
        settings_menu.add_separator()
        settings_menu.add_command(label="About", command=self.show_about)

        # ------------------------------------------------------------------------
        # SECTION: Status Bar (Top)
        # ------------------------------------------------------------------------
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=6)

        self.git_label = ttk.Label(top, text="Git Status: Checking...")
        self.git_label.grid(row=0, column=0, sticky="w", padx=(0, 12))

        self.gh_label = ttk.Label(top, text="GitHub Authentication: Checking...")
        self.gh_label.grid(row=0, column=1, sticky="w", padx=(0, 12))

        self.token_label = ttk.Label(top, text="Token Status: Checking...")
        self.token_label.grid(row=0, column=2, sticky="w", padx=(0, 12))

        self.net_label = ttk.Label(top, text="Network Status: Checking...")
        self.net_label.grid(row=0, column=3, sticky="w", padx=(0, 12))

        self.mode_label = ttk.Label(top, text=f"Mode: {DEFAULT_MODE}")
        self.mode_label.grid(row=0, column=4, sticky="w", padx=(0, 12))

        # ------------------------------------------------------------------------
        # SECTION: Control Bar (Buttons, Search, Export)
        # ------------------------------------------------------------------------
        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x", padx=8, pady=6)

        self.refresh_btn = ttk.Button(ctrl, text="Refresh", command=self.reload_status_async)
        self.refresh_btn.grid(row=0, column=0, padx=4)

        self.token_btn = ttk.Button(ctrl, text="🔑 Token", command=self.token_info_or_setup)
        self.token_btn.grid(row=0, column=1, padx=4)
        
        self.stats_btn = ttk.Button(ctrl, text="📊 Stats", command=self.show_stats)
        self.stats_btn.grid(row=0, column=2, padx=4)

        # Export section
        self.export_format_var = tk.StringVar(value=self.cfg.get("export_format", "txt"))
        ttk.Label(ctrl, text="Export:").grid(row=0, column=3, padx=(12, 4))
        
        self.export_csv_radio = ttk.Radiobutton(ctrl, text="CSV", variable=self.export_format_var, value="csv")
        self.export_csv_radio.grid(row=0, column=4, padx=2)
        
        self.export_txt_radio = ttk.Radiobutton(ctrl, text="TXT", variable=self.export_format_var, value="txt")
        self.export_txt_radio.grid(row=0, column=5, padx=2)
        
        self.export_btn = ttk.Button(ctrl, text="Export View", command=self.export_current_view_async)
        self.export_btn.grid(row=0, column=6, padx=4)

        # Search section
        ttk.Label(ctrl, text="Search:").grid(row=0, column=7, padx=(12, 4))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(ctrl, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=8, padx=4)
        self.search_entry.bind("<Return>", lambda e: self.apply_search_filter())

        # Filter section
        self.filter_var = tk.StringVar(value="All")
        ttk.Label(ctrl, text="Filter:").grid(row=0, column=9, padx=(12, 4))
        self.filter_combo = ttk.Combobox(ctrl, textvariable=self.filter_var, 
                                         values=["All", "Public", "Private", "Forks", "Owned"], width=12)
        self.filter_combo.grid(row=0, column=10, padx=4)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_search_filter())

        # ------------------------------------------------------------------------
        # SECTION: Main Container (Vertical Split: Content | Diagnostics)
        # ------------------------------------------------------------------------
        main_paned = ttk.Panedwindow(self, orient="vertical")
        main_paned.pack(fill="both", expand=True, padx=8, pady=6)

        # Top section: Tabs + Right Panel using GRID
        top_section = ttk.Frame(main_paned)
        main_paned.add(top_section, weight=3)

        # Configure grid weights
        top_section.grid_rowconfigure(0, weight=1)
        top_section.grid_columnconfigure(0, weight=3)
        top_section.grid_columnconfigure(1, weight=0, minsize=350)

        # Left side: Tabs
        self.tab_control = ttk.Notebook(top_section)
        self.tab_control.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        # Tab 0: Welcome
        self.tab_welcome = WelcomeTab(self.tab_control)
        self.tab_control.add(self.tab_welcome, text="Welcome")

        # Tab 1: My Repos / Public Browse
        self.tab_my = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_my, text="My Repos")
        self.table_my = RepoTable(self.tab_my)
        self.table_my.pack(fill="both", expand=True)

        # Tab 2: Organization Repos
        self.tab_orgs = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_orgs, text="Organization Repos")
        self.table_orgs = RepoTable(self.tab_orgs)
        self.table_orgs.pack(fill="both", expand=True)

        # Tab 3: Starred
        self.tab_starred = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_starred, text="Starred")
        self.table_starred = RepoTable(self.tab_starred)
        self.table_starred.pack(fill="both", expand=True)

        # Progress callbacks
        def set_text_progress(self, total, downloaded, message=""):
            try:
                pct = int((downloaded / total) * 100) if total else 0
                msg = f"[Download] {downloaded}/{total} ({pct}%) {message}"
                self._append_diag(msg)
            except Exception:
                pass

        def clear_text_progress(self):
            try:
                self._append_diag("[Download] Completed")
            except Exception:
                pass

        try:
            self._set_text_progress_impl = set_text_progress.__get__(self)
            self._clear_text_progress_impl = clear_text_progress.__get__(self)
        except Exception:
            self._set_text_progress_impl = lambda total, downloaded, message='': None
            self._clear_text_progress_impl = lambda: None

        # Tab 4: Download From Others
        self.tab_download_others = ExternalDownloadTab(
            self.tab_control,
            diag_append=self._append_diag,
            token_getter=get_token,
            progress_setter=self._set_text_progress_impl,
            progress_clearer=self._clear_text_progress_impl,
        )
        self.tab_control.add(self.tab_download_others, text="Download From Others")

        # Tab 5: Creation Lab (SAFE IN v2.0.0!)
        self.tab_creation_lab = CreationLabTab(
            self.tab_control,
            diag_append=self._append_diag
        )
        self.tab_control.add(self.tab_creation_lab, text="Creation Lab")

        # ------------------------------------------------------------------------
        # SECTION: Right Panel (Rate Limit, Details, Actions)
        # ------------------------------------------------------------------------
        right = tk.Frame(top_section, bg="lightgray", relief="raised", borderwidth=2)
        right.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        
        print("DEBUG: Right panel created and gridded to column 1")

        # Configure right panel internal layout
        right.grid_rowconfigure(0, weight=0)
        right.grid_rowconfigure(1, weight=1)
        right.grid_rowconfigure(2, weight=0)
        right.grid_columnconfigure(0, weight=1)

        # Rate limit display panel
        self.rate_limit_widget = RateLimitWidget(right, diag_append=self._append_diag)
        self.rate_limit_widget.grid(row=0, column=0, sticky="ew", padx=4, pady=4)

        # Repository details
        details_frame = ttk.LabelFrame(right, text="Repository Details")
        details_frame.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)

        details_container = ttk.Frame(details_frame)
        details_container.pack(fill="both", expand=True, padx=4, pady=4)

        self.details_text = tk.Text(details_container, wrap="word", width=35)
        self.details_text.pack(side="left", fill="both", expand=True)
        self.details_text.configure(state="disabled")

        details_scroll = ttk.Scrollbar(details_container, orient="vertical", command=self.details_text.yview)
        details_scroll.pack(side="right", fill="y")
        self.details_text.configure(yscrollcommand=details_scroll.set)

        # ----------------------------------------------------------------
        # SECTION: Action Tabs (Icon-only tabs for compact layout)
        # Replaces old Actions frame + Danger Zone
        # ----------------------------------------------------------------
        actions_notebook = ttk.Notebook(right)
        actions_notebook.grid(row=2, column=0, sticky="nsew", padx=4, pady=4)
        
        # ---- Tab 1: ⭐ Quick Actions ----
        actions_tab = ttk.Frame(actions_notebook, padding=4)
        actions_notebook.add(actions_tab, text=" ⭐ ")
        
        self.open_btn = ttk.Button(actions_tab, text="🌐 Open in Browser", 
                                   command=self.open_selected_in_browser)
        self.open_btn.pack(fill="x", pady=2)
        
        self.clone_btn = ttk.Button(actions_tab, text="📥 Clone Selected", 
                                    command=self.clone_selected_async)
        self.clone_btn.pack(fill="x", pady=2)
        
        self.zip_btn = ttk.Button(actions_tab, text="📦 Download ZIP", 
                                  command=self.download_zip_selected_async)
        self.zip_btn.pack(fill="x", pady=2)
        
        self.star_btn = ttk.Button(actions_tab, text="☆ Star Repo", 
                                   command=self.toggle_star_async)
        self.star_btn.pack(fill="x", pady=2)
        
        # ---- Tab 2: 🔧 Manage Repo ----
        manage_tab = ttk.Frame(actions_notebook, padding=4)
        actions_notebook.add(manage_tab, text=" 🔧 ")
        
        self.privacy_btn = ttk.Button(manage_tab, text="🔒 Toggle Privacy", 
                                      command=self.toggle_privacy_async)
        self.privacy_btn.pack(fill="x", pady=2)
        
        self.fork_btn = ttk.Button(manage_tab, text="🔀 Fork Repo", 
                                   command=self.fork_repo_async)
        self.fork_btn.pack(fill="x", pady=2)
        
        self.rename_btn = ttk.Button(manage_tab, text="✏️ Rename Repo", 
                                     command=self.rename_repo_async)
        self.rename_btn.pack(fill="x", pady=2)
        
        # ---- Tab 3: ⚠️ Danger Zone ----
        danger_tab = ttk.Frame(actions_notebook, padding=4)
        actions_notebook.add(danger_tab, text=" ⚠️ ")
        
        self.delete_btn = ttk.Button(danger_tab, text="🗑️ Delete Repository", 
                                     command=self.delete_repo_async)
        self.delete_btn.pack(fill="x", pady=2)

        # ------------------------------------------------------------------------
        # SECTION: Diagnostics Panel (Bottom - Resizable)
        # ------------------------------------------------------------------------
        diag_section = ttk.Frame(main_paned)
        main_paned.add(diag_section, weight=1)

        diag_header = ttk.Frame(diag_section)
        diag_header.pack(fill="x", padx=4, pady=(4, 0))

        diag_label = ttk.Label(diag_header, text="Diagnostics Console", 
                               font=("TkDefaultFont", 9, "bold"))
        diag_label.pack(side="left")

        diag_hint = ttk.Label(diag_header, text="(drag divider above to resize ↕)", 
                             font=("TkDefaultFont", 8), foreground="gray")
        diag_hint.pack(side="left", padx=(8, 0))

        # Diagnostics text with scrollbar
        diag_frame = ttk.Frame(diag_section)
        diag_frame.pack(fill="both", expand=True, padx=4, pady=4)

        self.diag = tk.Text(diag_frame, wrap="word")
        self.diag.pack(side="left", fill="both", expand=True)
        self.diag.insert("end", "Diagnostics log:\n")
        self.diag.configure(state="disabled")

        diag_scroll = ttk.Scrollbar(diag_frame, orient="vertical", command=self.diag.yview)
        diag_scroll.pack(side="right", fill="y")
        self.diag.configure(yscrollcommand=diag_scroll.set)

        # ------------------------------------------------------------------------
        # SECTION: Event Bindings
        # ------------------------------------------------------------------------
        self.table_my.tree.bind("<<TreeviewSelect>>", lambda e: self.on_selection_changed(self.table_my))
        self.table_orgs.tree.bind("<<TreeviewSelect>>", lambda e: self.on_selection_changed(self.table_orgs))
        self.table_starred.tree.bind("<<TreeviewSelect>>", lambda e: self.on_selection_changed(self.table_starred))

        # ------------------------------------------------------------------------
        # SECTION: State Variables
        # ------------------------------------------------------------------------
        self.repos_my: List[Dict] = []
        self.repos_orgs: List[Dict] = []
        self.repos_starred: List[Dict] = []
        self.current_starred_status: Optional[bool] = None

        self._table_row_height = 24
        self._table_fraction = 0.5

        # Dynamic table height adjustment
        def _adjust_tables(event=None):
            try:
                nb_h = self.tab_control.winfo_height()
                available = max(120, nb_h - 20)
                for tbl in (getattr(self, 'table_my', None), getattr(self, 'table_starred', None), getattr(self, 'table_orgs', None)):
                    if not tbl:
                        continue
                    try:
                        if hasattr(tbl, 'set_dynamic_height'):
                            tbl.set_dynamic_height(available, row_height=self._table_row_height, fraction=self._table_fraction)
                        else:
                            rows = max(3, int((available * self._table_fraction) / self._table_row_height))
                            tbl.tree.configure(height=rows)
                    except Exception:
                        pass
            except Exception:
                pass

        self.bind('<Configure>', _adjust_tables)
        self.after(150, _adjust_tables)

        # ------------------------------------------------------------------------
        # SECTION: Initialization
        # ------------------------------------------------------------------------
        self.reload_lock = threading.Lock()
        self.after(100, self.reload_status_async)
        self.after(500, self.update_rate_limit_async)
        
               # UPDATED IN v2.0.2: New features
        self._append_diag("🔧 Right panel initialized (Tabbed Actions - v2.0.2)")
        self._append_diag("⭐ Actions: Open, Clone, ZIP, Star")
        self._append_diag("🔧 Manage: Toggle Privacy, Fork, Rename")
        self._append_diag("⚠️ Danger: Delete Repository")
        self._append_diag("🛡️ Safety checks enabled - prevents repo overwrites!")
        self._append_diag("✅ All features initialized successfully!")
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ========================================================================
    # SECTION: Window Lifecycle Methods
    # ========================================================================
    def on_closing(self):
        """Save configuration before closing."""
        try:
            self.cfg.set("window_geometry", self.geometry())
            self.cfg.set("last_tab", self.tab_control.index(self.tab_control.select()))
            self.cfg.set("export_format", self.export_format_var.get())
        except Exception:
            pass
        self.destroy()

    # ========================================================================
    # SECTION: Dialog Methods
    # ========================================================================
    def show_settings_dialog(self):
        """Show settings dialog for configuring public browse user."""
        dialog = tk.Toplevel(self)
        dialog.title("Settings")
        dialog.geometry("400x150")
        dialog.transient(self)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Default Public Browse Username:", font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=(0, 10))
        
        info = ttk.Label(frame, text="When no token is present, Tab 1 will show public repos for this user.", 
                        wraplength=350, justify="left")
        info.pack(anchor="w", pady=(0, 10))
        
        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(entry_frame, text="Username:").pack(side="left", padx=(0, 10))
        username_var = tk.StringVar(value=self.cfg.get("default_public_user", "kindle15"))
        username_entry = ttk.Entry(entry_frame, textvariable=username_var, width=30)
        username_entry.pack(side="left", fill="x", expand=True)
        
        def save_settings():
            new_user = username_var.get().strip()
            if new_user:
                self.cfg.set("default_public_user", new_user)
                self._append_diag(f"Updated default public browse user to: {new_user}")
                messagebox.showinfo("Settings Saved", f"Default user set to: {new_user}\n\nReload Tab 1 to see changes.")
                dialog.destroy()
            else:
                messagebox.showwarning("Invalid Input", "Username cannot be empty.")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Save", command=save_settings).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="right")
        
        username_entry.focus()
        username_entry.select_range(0, tk.END)

    def show_about(self):
        """Show about dialog with copyright (UPDATED IN v2.0.2)."""
        about_text = """GithubTool v2.0.2

A comprehensive GitHub repository management tool.

New in v2.0.2:
• 🎯 Tabbed action panel (⭐ / 🔧 / ⚠️)
• 🔑 Token button (status + setup)
• 📊 Stats button (dump to console)
• 🔒 Toggle Privacy (Public ↔ Private)
• 🔀 Fork Repo (to your account)
• ✏️ Rename Repo (changes URL)
• 📋 Console-first design (less popups!)

Previous:
v2.0.1: Push to Branch, ZIP fix, Delete repo
v2.0.0: Safety checks, prevent overwrites

Features:
• Smart public browsing (no token required)
• Star/unstar repositories ⭐
• Creation Lab with README/LICENSE templates
• Export to CSV/TXT
• Download repos, releases, and assets
• Space-efficient tabbed layout
• Resizable diagnostics panel

(c) kindle15 / 2026

Created with ❤️ using Python & Tkinter"""
        
        messagebox.showinfo("About GithubTool", about_text)
    # ========================================================================
    # SECTION: Diagnostics & Progress Methods
    # ========================================================================
    def _append_diag(self, text: str) -> None:
        """Append message to diagnostics log."""
        _append_diag_widget(self.diag, text)

    def _set_text_progress_impl(self, total: int, downloaded: int, message: str = "") -> None:
        """Update download progress in diagnostics."""
        try:
            pct = int((downloaded / total) * 100) if total and total > 0 else 0
            msg = f"[Download] {downloaded}/{total} ({pct}%) {message}"
            self._append_diag(msg)
        except Exception:
            pass

    def _clear_text_progress_impl(self) -> None:
        """Clear download progress indicator."""
        try:
            self._append_diag("[Download] Completed")
        except Exception:
            pass

    # ========================================================================
    # SECTION: Rate Limit Methods
    # ========================================================================
    def update_rate_limit_async(self) -> None:
        """Update rate limit display asynchronously."""
        threading.Thread(target=self.update_rate_limit, daemon=True).start()

    def update_rate_limit(self) -> None:
        """Fetch and display current GitHub API rate limit."""
        try:
            self.rate_limit_widget.refresh()
        except Exception as e:
            self._append_diag(f"Rate limit update failed: {e}")

    # ========================================================================
    # SECTION: Repository Fetch Methods
    # ========================================================================
    def reload_status_async(self) -> None:
        threading.Thread(target=self.reload_status, daemon=True).start()

    def reload_status(self) -> None:
        try:
            git_status, git_details = self._check_git()
            self.git_label.config(text=f"Git Status: {git_status}")
            self._append_diag(f"Git check: {git_details}")
        except Exception as e:
            self._append_diag(f"Git check failed: {e}")
        try:
            net_status, net_details = self._check_network()
            self.net_label.config(text=f"Network Status: {net_status}")
            self._append_diag(f"Network check: {net_details}")
        except Exception as e:
            self._append_diag(f"Network check failed: {e}")
        try:
            token, source = get_token()
        except Exception as e:
            token, source = None, f"get_token() raised: {e}"
        if token:
            self.gh_label.config(text="GitHub Authentication: Authenticated")
            self.token_label.config(text=f"Token: {_mask_token(token)}")
            self._append_diag(f"Auth check: token found ({source})")
            self.tab_control.tab(1, text="My Repos")
            self.star_btn.config(state="normal")
            self._append_diag("Fetching your repositories (authenticated)...")
            try:
                repos = fetch_user_repos(token)
                self.repos_my = repos
                self.table_my.populate(repos)
                self._append_diag(f"Fetched {len(repos)} repositories (my repos)")
                self.after(100, self.update_rate_limit_async)
            except GitHubFetchError as e:
                self._append_diag(f"Fetch failed: {e}")
            except Exception as e:
                self._append_diag(f"Unexpected fetch error: {e}")
            threading.Thread(target=self._fetch_starred_and_orgs, args=(token,), daemon=True).start()
        else:
            self.gh_label.config(text="GitHub Authentication: Not Authenticated")
            self.token_label.config(text=f"Token Status: Not Detected ({source})")
            self._append_diag(f"Auth check: {source}")
            default_user = self.cfg.get("default_public_user", "kindle15")
            self.tab_control.tab(1, text=f"Public Browse: {default_user}")
            self.star_btn.config(state="disabled")
            self._append_diag("ℹ️ Star functionality requires GitHub token")
            self._append_diag(f"Fetching public repos for {default_user} (no token required)...")
            try:
                repos = self._fetch_public_repos_for_user(default_user, None)
                self.repos_my = repos
                self.table_my.populate(repos)
                self._append_diag(f"Fetched {len(repos)} public repositories for {default_user}")
            except Exception as e:
                self._append_diag(f"Failed to fetch public repos for {default_user}: {e}")

    def _fetch_public_repos_for_user(self, username: str, token: Optional[str]) -> List[Dict]:
        repos: List[Dict] = []
        page = 1
        while True:
            url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}&sort=updated"
            try:
                data, hdrs = _http_get_json(url, token)
                if isinstance(data, list):
                    repos.extend(data)
                    link = hdrs.get("Link", "")
                    if 'rel="next"' not in link:
                        break
                    page += 1
                else:
                    break
            except Exception as e:
                self._append_diag(f"Failed to fetch public repos for {username}: {e}")
                break
        return repos

    def _fetch_starred_and_orgs(self, token: str) -> None:
        try:
            starred = self._fetch_starred(token)
            self.repos_starred = starred
            self.table_starred.populate(starred)
            self._append_diag(f"Fetched {len(starred)} starred repositories")
            self.after(100, self.update_rate_limit_async)
        except Exception as e:
            self._append_diag(f"Starred fetch failed: {e}")
        try:
            org_repos: List[Dict] = []
            orgs = self._fetch_user_orgs(token)
            for org in orgs:
                name = org.get("login")
                if not name:
                    continue
                try:
                    repos = self._fetch_org_repos(token, name)
                    org_repos.extend(repos)
                except Exception as e:
                    self._append_diag(f"Failed to fetch repos for org {name}: {e}")
            self.repos_orgs = org_repos
            self.table_orgs.populate(org_repos)
            self._append_diag(f"Fetched {len(org_repos)} organization repositories")
            self.after(100, self.update_rate_limit_async)
        except Exception as e:
            self._append_diag(f"Org fetch failed: {e}")

    def _check_git(self) -> Tuple[str, str]:
        try:
            import shutil
            git_path = shutil.which("git")
            if git_path:
                return "Installed and Ready", f"git at {git_path}"
            return "Not Installed or Not in PATH", "git not found"
        except Exception as e:
            return "Unknown", str(e)

    def _check_network(self) -> Tuple[str, str]:
        if network_utils and hasattr(network_utils, "check_network"):
            try:
                ok, details = network_utils.check_network()
                return ("Connected" if ok else "Offline or Unreachable", details)
            except Exception as e:
                return "Offline or Unreachable", str(e)
        try:
            import socket
            sock = socket.create_connection(("api.github.com", 443), timeout=2.0)
            sock.close()
            return "Connected", "api.github.com reachable"
        except Exception as e:
            return "Offline or Unreachable", str(e)

    def _fetch_starred(self, token: str) -> List[Dict]:
        repos: List[Dict] = []
        page = 1
        while True:
            url = f"https://api.github.com/user/starred?per_page=100&page={page}"
            data, hdrs = _http_get_json(url, token)
            if not isinstance(data, list):
                break
            repos.extend(data)
            link = hdrs.get("Link", "")
            if 'rel="next"' not in link:
                break
            page += 1
        return repos

    def _fetch_user_orgs(self, token: str) -> List[Dict]:
        url = "https://api.github.com/user/orgs"
        data, _ = _http_get_json(url, token)
        if isinstance(data, list):
            return data
        return []

    def _fetch_org_repos(self, token: str, org: str) -> List[Dict]:
        repos: List[Dict] = []
        page = 1
        while True:
            url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}"
            data, hdrs = _http_get_json(url, token)
            if not isinstance(data, list):
                break
            repos.extend(data)
            link = hdrs.get("Link", "")
            if 'rel="next"' not in link:
                break
            page += 1
        return repos

    # ========================================================================
    # SECTION: Selection & Display Methods
    # ========================================================================
    def on_selection_changed(self, table: RepoTable) -> None:
        items = table.selected_items()
        if not items:
            self._set_details_text("No repository selected.")
            self.current_starred_status = None
            self.star_btn.config(text="☆ Star Repo")
            return
        vals = items[0]
        name, private, fork, full_name, html_url = vals
        repo_obj = self._find_repo_by_full_name(full_name)
        if repo_obj:
            desc = repo_obj.get("description", "") or ""
            default_branch = repo_obj.get("default_branch", "main")
            topics = ", ".join(repo_obj.get("topics", []) or [])
            details = (f"Name: {name}\nFull name: {full_name}\nPrivate: {private}\nFork: {fork}\n"
                      f"Default branch: {default_branch}\nURL: {html_url}\n\nDescription:\n{desc}\n\nTopics: {topics}")
            self._set_details_text(details)
            self._check_star_status_async(full_name)
        else:
            self._set_details_text(f"Name: {name}\nFull name: {full_name}\nURL: {html_url}\n\nDetails not available in memory.")
            self.current_starred_status = None
            self.star_btn.config(text="☆ Star Repo")

    def _set_details_text(self, text: str) -> None:
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("end", text)
        self.details_text.configure(state="disabled")

    def _find_repo_by_full_name(self, full_name: str) -> Optional[Dict]:
        for lst in (self.repos_my, self.repos_orgs, self.repos_starred):
            for r in lst:
                if r.get("full_name") == full_name:
                    return r
        return None

    def _get_current_repo_from_active_tab(self) -> Optional[Dict]:
        current_tab_idx = self.tab_control.index(self.tab_control.select())
        if current_tab_idx == 0 or current_tab_idx == 5:
            return None
        elif current_tab_idx == 4:
            return self.tab_download_others.get_current_repo()
        elif current_tab_idx == 1:
            items = self.table_my.selected_items()
        elif current_tab_idx == 2:
            items = self.table_orgs.selected_items()
        elif current_tab_idx == 3:
            items = self.table_starred.selected_items()
        else:
            return None
        if items:
            full_name = items[0][3]
            return self._find_repo_by_full_name(full_name)
        return None

    # ========================================================================
    # SECTION: Star/Unstar Methods
    # ========================================================================
    def _check_star_status_async(self, full_name: str) -> None:
        threading.Thread(target=self._check_star_status, args=(full_name,), daemon=True).start()

    def _check_star_status(self, full_name: str) -> None:
        try:
            token, _ = get_token()
            if not token:
                self.current_starred_status = None
                return
            parts = full_name.split('/')
            if len(parts) != 2:
                return
            owner, repo = parts
            is_starred = check_if_starred(owner, repo, token)
            self.current_starred_status = is_starred
            if is_starred:
                self.star_btn.config(text="⭐ Unstar Repo")
            else:
                self.star_btn.config(text="☆ Star Repo")
        except Exception as e:
            self._append_diag(f"Failed to check star status: {e}")
            self.current_starred_status = None

    def toggle_star_async(self) -> None:
        threading.Thread(target=self.toggle_star, daemon=True).start()

    def toggle_star(self) -> None:
        try:
            token, _ = get_token()
            if not token:
                self._append_diag("⚠️ Cannot star repo: Requires authentication")
                messagebox.showwarning("Authentication Required", "Star/Unstar requires a GitHub token.")
                return
            repo = self._get_current_repo_from_active_tab()
            if not repo:
                self._append_diag("⚠️ No repository selected")
                return
            full_name = repo.get("full_name")
            if not full_name:
                return
            parts = full_name.split('/')
            if len(parts) != 2:
                return
            owner, repo_name = parts
            is_starred = check_if_starred(owner, repo_name, token)
            if is_starred:
                unstar_repository(owner, repo_name, token)
                self._append_diag(f"☆ Unstarred {full_name}")
                self.star_btn.config(text="☆ Star Repo")
            else:
                star_repository(owner, repo_name, token)
                self._append_diag(f"✅ Starred {full_name}")
                self.star_btn.config(text="⭐ Unstar Repo")
            self.after(100, self.update_rate_limit_async)
        except Exception as e:
            self._append_diag(f"⚠️ Star failed: {e}")
            messagebox.showerror("Star Failed", f"Star operation failed:\n{e}")

    # ========================================================================
    # SECTION: Danger Zone - Delete Repository
    # Added in: v2.0.1
    # ========================================================================
    
    def delete_repo_async(self) -> None:
        """Delete repo - confirmation dialogs on main thread, delete on background thread."""
        repo = self._get_current_repo_from_active_tab()
        if not repo:
            self._append_diag("⚠️ Delete: No repository selected")
            messagebox.showwarning("Delete Repo", "No repository selected.")
            return
        
        full_name = repo.get("full_name", "")
        html_url = repo.get("html_url", "")
        private = "Private" if repo.get("private", False) else "Public"
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        size = repo.get("size", 0)
        
        self._append_diag(f"🗑️ Delete requested for: {full_name}")
        
        # Get token first
        token, source = get_token()
        if not token:
            self._append_diag("❌ Delete: No token available")
            messagebox.showerror(
                "Authentication Required",
                "Deleting repositories requires a GitHub token with delete permissions."
            )
            return
        
        # ================================================================
        # SAFEGUARD 1: First Confirmation - Show repo details
        # ================================================================
        confirm1 = messagebox.askyesno(
            "⚠️ Delete Repository?",
            f"Are you sure you want to delete this repository?\n\n"
            f"📦 Repository: {full_name}\n"
            f"🔒 Privacy: {private}\n"
            f"⭐ Stars: {stars}\n"
            f"🔱 Forks: {forks}\n"
            f"📊 Size: {size} KB\n"
            f"🌐 URL: {html_url}\n\n"
            f"This will permanently delete the repository\n"
            f"and all its contents from GitHub.",
            icon="warning"
        )
        
        if not confirm1:
            self._append_diag(f"🗑️ Delete CANCELLED by user (dialog 1): {full_name}")
            return
        
        # ================================================================
        # SAFEGUARD 2: Final Confirmation - CANNOT BE UNDONE
        # ================================================================
        confirm2 = messagebox.askyesno(
            "🚨 THIS CANNOT BE UNDONE!",
            f"⚠️ FINAL WARNING ⚠️\n\n"
            f"You are about to PERMANENTLY DELETE:\n\n"
            f"    {full_name}\n\n"
            f"This action CANNOT be undone!\n"
            f"All code, issues, PRs, and wiki will be lost.\n\n"
            f"Are you absolutely sure?",
            icon="warning"
        )
        
        if not confirm2:
            self._append_diag(f"🗑️ Delete CANCELLED by user (dialog 2): {full_name}")
            return
        
        self._append_diag(f"⚠️ User confirmed deletion of {full_name}")
        
        # Parse owner/repo
        parts = full_name.split('/')
        if len(parts) != 2:
            self._append_diag(f"❌ Delete: Invalid repo format: {full_name}")
            messagebox.showerror("Error", f"Invalid repository format: {full_name}")
            return
        
        owner, repo_name = parts
        
        # Delete on BACKGROUND THREAD
        def _do_delete():
            try:
                self._append_diag(f"🗑️ Deleting {full_name} from GitHub...")
                
                url = f"https://api.github.com/repos/{owner}/{repo_name}"
                headers = {
                    "User-Agent": "GithubTool/2.0.2",
                    "Authorization": f"token {token}"
                }
                
                req = urllib.request.Request(url, headers=headers, method='DELETE')
                with urllib.request.urlopen(req, timeout=15) as resp:
                    if resp.status == 204:
                        self._append_diag(f"=" * 60)
                        self._append_diag(f"🗑️ REPOSITORY DELETED SUCCESSFULLY")
                        self._append_diag(f"   Repository: {full_name}")
                        self._append_diag(f"   Status: Permanently removed from GitHub")
                        self._append_diag(f"=" * 60)
                        
                        messagebox.showinfo(
                            "Repository Deleted",
                            f"Repository deleted successfully.\n\n"
                            f"📦 {full_name}\n\n"
                            f"The repository has been permanently\n"
                            f"removed from GitHub.\n\n"
                            f"Click Refresh to update the repo list."
                        )
                    else:
                        self._append_diag(f"⚠️ Unexpected response: {resp.status}")
                        messagebox.showwarning(
                            "Unexpected Response",
                            f"Server returned status {resp.status}.\n"
                            f"The repository may or may not have been deleted.\n"
                            f"Please check GitHub to confirm."
                        )
            
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    self._append_diag(f"❌ Delete FORBIDDEN: Token lacks delete permission")
                    messagebox.showerror(
                        "Permission Denied",
                        f"Your token does not have permission to delete repositories.\n\n"
                        f"Required scope: 'delete_repo'\n\n"
                        f"Generate a new token with the 'delete_repo' scope at:\n"
                        f"https://github.com/settings/tokens"
                    )
                elif e.code == 404:
                    self._append_diag(f"❌ Delete: Repository not found (already deleted?)")
                    messagebox.showerror(
                        "Not Found",
                        f"Repository {full_name} was not found.\n\n"
                        f"It may have already been deleted."
                    )
                else:
                    self._append_diag(f"❌ Delete HTTP Error: {e.code} - {e.reason}")
                    messagebox.showerror("Delete Failed", f"HTTP Error {e.code}: {e.reason}")
            
            except Exception as e:
                self._append_diag(f"❌ Delete failed: {e}")
                messagebox.showerror("Delete Failed", f"Failed to delete repository:\n\n{e}")
        
        threading.Thread(target=_do_delete, daemon=True).start()

    # ========================================================================
    # SECTION: Repository Action Methods
    # ========================================================================
   
    def open_selected_in_browser(self) -> None:
        """Open selected repository in web browser."""
        repo = self._get_current_repo_from_active_tab()
        if not repo:
            messagebox.showwarning("Open", "No repository selected.")
            return
        html_url = repo.get("html_url")
        if html_url:
            self._append_diag(f"Opening {html_url} in browser")
            webbrowser.open(html_url)
        else:
            messagebox.showwarning("Open", "Repository URL not available.")

    def clone_selected_async(self) -> None:
        """Clone repo - dialog on main thread, clone on background thread."""
        repo = self._get_current_repo_from_active_tab()
        if not repo:
            self._append_diag("⚠️ Clone: No repository selected")
            messagebox.showwarning("Clone", "No repository selected.")
            return
        
        full_name = repo.get("full_name", "unknown")
        self._append_diag(f"📥 Clone: Starting for {full_name}")
        
        # Dialog on MAIN THREAD
        dest = filedialog.askdirectory(title="Select destination folder")
        if not dest:
            self._append_diag("📥 Clone: No folder selected, cancelled")
            return
        
        url = repo.get("html_url")
        name = repo.get("name")
        clone_path = os.path.join(dest, name)
        
        self._append_diag(f"📥 Clone: {url}")
        self._append_diag(f"📥 Clone: Destination = {clone_path}")
        
        # Clone on BACKGROUND THREAD (no dialogs in thread)
        def _do_clone():
            try:
                cmd = ["git", "clone", "--depth", "1", url, clone_path]
                proc = subprocess.run(cmd, capture_output=True, text=True)
                if proc.returncode != 0:
                    self._append_diag(f"❌ Clone failed: {proc.stderr.strip()}")
                    messagebox.showerror("Clone Failed", proc.stderr.strip())
                else:
                    self._append_diag(f"✅ Clone completed: {clone_path}")
                    messagebox.showinfo("Clone Complete", f"Cloned to:\n{clone_path}")
            except Exception as e:
                self._append_diag(f"❌ Clone exception: {e}")
                messagebox.showerror("Clone Failed", f"Exception: {e}")
        
        threading.Thread(target=_do_clone, daemon=True).start()
        
    def download_zip_selected_async(self) -> None:
        """Download ZIP - dialogs on main thread, download on background thread."""
        repo = self._get_current_repo_from_active_tab()
        if not repo:
            self._append_diag("⚠️ ZIP Download: No repository selected")
            messagebox.showwarning("Download ZIP", "No repository selected.")
            return
        
        full_name = repo.get("full_name")
        self._append_diag(f"📦 ZIP Download: Starting for {full_name}")
        
        # Dialog 1: Ask for branch (MAIN THREAD)
        branch = simpledialog.askstring("Source Archive", "Branch (blank for default):")
        if branch is None:
            self._append_diag("📦 ZIP Download: Cancelled by user")
            return
        if not branch:
            branch = repo.get("default_branch") or "main"
        
        self._append_diag(f"📦 ZIP Download: Branch = {branch}")
        
        # Dialog 2: Ask for save folder (MAIN THREAD)
        out_dir = filedialog.askdirectory(title="Select folder to save ZIP")
        if not out_dir:
            self._append_diag("📦 ZIP Download: No folder selected, cancelled")
            return
        
        out_path = os.path.join(out_dir, f"{full_name.replace('/', '_')}_{branch}.zip")
        zip_url = f"https://github.com/{full_name}/archive/refs/heads/{branch}.zip"
        
        self._append_diag(f"📦 ZIP Download: URL = {zip_url}")
        self._append_diag(f"📦 ZIP Download: Saving to {out_path}")
        
        # Actual download on BACKGROUND THREAD (no dialogs in thread)
        def _do_download():
            try:
                # NEW (with auth):
                token, _ = get_token()

                headers = {'User-Agent': 'GithubTool/2.0.0'}
                if token:
                    headers['Authorization'] = f'token {token}'
                    
                req = urllib.request.Request(zip_url, headers=headers)
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = resp.read()
                    self._append_diag(f"📦 ZIP Download: Received {len(data):,} bytes")
                    with open(out_path, 'wb') as fh:
                        fh.write(data)
                self._append_diag(f"✅ ZIP saved to: {out_path}")
                messagebox.showinfo("Download Complete", f"Downloaded to:\n{out_path}")
            except urllib.error.HTTPError as e:
                self._append_diag(f"❌ ZIP Download HTTP Error: {e.code} - {e.reason}")
                if e.code == 404:
                    messagebox.showerror(
                        "Download Failed",
                        f"Branch '{branch}' not found!\n\n"
                        f"URL: {zip_url}\n\n"
                        f"Check the branch name is correct.\n"
                        f"Common branches: main, master"
                    )
                else:
                    messagebox.showerror("Download Failed", f"HTTP Error {e.code}: {e.reason}")
            except Exception as e:
                self._append_diag(f"❌ ZIP Download failed: {e}")
                messagebox.showerror("Download Failed", f"Failed: {e}")
        
        threading.Thread(target=_do_download, daemon=True).start()

    # ========================================================================
    # SECTION: Token & Stats Methods (Added in v2.0.2)
    # ========================================================================
    def token_info_or_setup(self) -> None:
        """Show token info via console if authenticated, or open GitHub token page if not."""
        from auth_token import TOKEN_FILENAME as token_filename
        token, source = get_token()
        
        if not token:
            self._append_diag("=" * 60)
            self._append_diag("🔑 TOKEN STATUS: Not authenticated")
            self._append_diag(f"   Source checked: {source}")
            self._append_diag("")
            self._append_diag("   ╔══════════════════════════════════════════╗")
            self._append_diag("   ║         HOW TO SET UP YOUR TOKEN        ║")
            self._append_diag("   ╚══════════════════════════════════════════╝")
            self._append_diag("")
            self._append_diag("   STEP 1: Create a token on GitHub")
            self._append_diag("     → Opening GitHub token page now...")
            self._append_diag("     → Select scopes:")
            self._append_diag("         ✅ repo (full control of private repos)")
            self._append_diag("         ✅ delete_repo (for Danger Zone)")
            self._append_diag("     → Click 'Generate token'")
            self._append_diag("     → COPY the token immediately!")
            self._append_diag("")
            self._append_diag("   STEP 2: Save the token (pick ONE method)")
            self._append_diag("")
            self._append_diag("   METHOD A - USB Drive (recommended):")
            self._append_diag("     1. Insert a USB flash drive")
            self._append_diag("     2. Create a text file on the ROOT of the drive")
            self._append_diag(f"     3. Name it exactly: {token_filename}")
            self._append_diag("     4. Paste your token as the ONLY content")
            self._append_diag("     5. Save and close")
            self._append_diag(f"     Example: E:\\{token_filename}")
            self._append_diag("     (Scans drives D: through Z: automatically)")
            self._append_diag("")
            self._append_diag("   METHOD B - Environment Variable:")
            self._append_diag("     Set GITHUB_TOKEN or GH_TOKEN:")
            self._append_diag("     Windows CMD:  set GITHUB_TOKEN=ghp_xxxx...")
            self._append_diag("     PowerShell:   $env:GITHUB_TOKEN='ghp_xxxx...'")
            self._append_diag("     Permanent:    System Properties → Environment Variables")
            self._append_diag("")
            self._append_diag("   STEP 3: Restart GithubTool or click [Refresh]")
            self._append_diag("=" * 60)
            webbrowser.open("https://github.com/settings/tokens/new")
        else:
            masked = _mask_token(token)
            self._append_diag("=" * 60)
            self._append_diag("🔑 TOKEN STATUS: Authenticated ✅")
            self._append_diag(f"   Token: {masked}")
            self._append_diag(f"   Source: {source}")
            self._append_diag("")
            
            # Quick token test - show username
            try:
                username = get_authenticated_user(token)
                self._append_diag(f"   User: {username}")
            except Exception as e:
                self._append_diag(f"   User: Could not verify ({e})")
            
            # Show rate limit too
            try:
                url = "https://api.github.com/rate_limit"
                data, _ = _http_get_json(url, token)
                core = data.get('resources', {}).get('core', {})
                remaining = core.get('remaining', 0)
                limit = core.get('limit', 0)
                self._append_diag(f"   Rate limit: {remaining}/{limit} remaining")
            except Exception:
                pass
            
            self._append_diag("=" * 60)
    
    def show_stats(self) -> None:
        """Dump stats for the current tab to the diagnostics console."""
        tab = self.tab_control.index(self.tab_control.select())
        
        if tab == 0:
            self._append_diag("📊 Stats: Welcome tab has no stats to show.")
            return
        elif tab == 1:
            data = self.repos_my
            tab_name = "My Repos"
        elif tab == 2:
            data = self.repos_orgs
            tab_name = "Organization Repos"
        elif tab == 3:
            data = self.repos_starred
            tab_name = "Starred Repos"
        elif tab == 4:
            data = self.tab_download_others.get_all_repos_for_export()
            tab_name = "Download From Others"
        elif tab == 5:
            self._append_diag("📊 Stats: Creation Lab has no stats to show.")
            return
        else:
            self._append_diag("📊 Stats: Unknown tab.")
            return
        
        if not data:
            self._append_diag(f"📊 Stats: No data in {tab_name}.")
            return
        
        total = len(data)
        public = sum(1 for r in data if not r.get("private", False))
        private = sum(1 for r in data if r.get("private", False))
        forks = sum(1 for r in data if r.get("fork", False))
        original = total - forks
        
        total_stars = sum(r.get("stargazers_count", 0) for r in data)
        total_forks = sum(r.get("forks_count", 0) for r in data)
        total_issues = sum(r.get("open_issues_count", 0) for r in data)
        total_size = sum(r.get("size", 0) for r in data)
        
        # Top languages
        lang_count: Dict[str, int] = {}
        for r in data:
            lang = r.get("language") or "Unknown"
            lang_count[lang] = lang_count.get(lang, 0) + 1
        top_langs = sorted(lang_count.items(), key=lambda x: x[1], reverse=True)[:5]
        lang_str = ", ".join(f"{lang} ({count})" for lang, count in top_langs)
        
        # Most starred
        most_starred = max(data, key=lambda r: r.get("stargazers_count", 0))
        most_starred_name = most_starred.get("full_name", most_starred.get("name", "?"))
        most_starred_count = most_starred.get("stargazers_count", 0)
        
        # Largest repo
        largest = max(data, key=lambda r: r.get("size", 0))
        largest_name = largest.get("full_name", largest.get("name", "?"))
        largest_size = largest.get("size", 0)
        
        # Format size
        if largest_size >= 1024:
            size_str = f"{largest_size / 1024:.1f} MB"
        else:
            size_str = f"{largest_size} KB"
        
        if total_size >= 1024:
            total_size_str = f"{total_size / 1024:.1f} MB"
        else:
            total_size_str = f"{total_size} KB"
        
        self._append_diag("=" * 60)
        self._append_diag(f"📊 STATS: {tab_name}")
        self._append_diag("=" * 60)
        self._append_diag(f"   Total repos:     {total}")
        self._append_diag(f"   Public:          {public}")
        self._append_diag(f"   Private:         {private}")
        self._append_diag(f"   Original:        {original}")
        self._append_diag(f"   Forked:          {forks}")
        self._append_diag(f"   ─────────────────────────")
        self._append_diag(f"   Total stars:     ⭐ {total_stars:,}")
        self._append_diag(f"   Total forks:     🔱 {total_forks:,}")
        self._append_diag(f"   Open issues:     ⚠️  {total_issues:,}")
        self._append_diag(f"   Total size:      📦 {total_size_str}")
        self._append_diag(f"   ─────────────────────────")
        self._append_diag(f"   Top languages:   {lang_str}")
        self._append_diag(f"   Most starred:    {most_starred_name} (⭐ {most_starred_count})")
        self._append_diag(f"   Largest repo:    {largest_name} ({size_str})")
        self._append_diag("=" * 60)

    # ========================================================================
    # SECTION: Manage Repo Methods (Added in v2.0.2)
    # ========================================================================
    def toggle_privacy_async(self) -> None:
        """Toggle repo privacy - runs on background thread."""
        repo = self._get_current_repo_from_active_tab()
        if not repo:
            self._append_diag("🔒 Toggle Privacy: No repository selected")
            return
        
        token, _ = get_token()
        if not token:
            self._append_diag("🔒 Toggle Privacy: No token available")
            return
        
        full_name = repo.get("full_name", "")
        is_private = repo.get("private", False)
        new_state = not is_private
        new_label = "Private" if new_state else "Public"
        old_label = "Private" if is_private else "Public"
        
        # Confirm on main thread
        confirm = messagebox.askyesno(
            "Toggle Privacy",
            f"Change repository privacy?\n\n"
            f"📦 {full_name}\n"
            f"🔒 Current: {old_label}\n"
            f"🔓 New: {new_label}\n\n"
            f"Continue?"
        )
        
        if not confirm:
            self._append_diag(f"🔒 Toggle Privacy: Cancelled for {full_name}")
            return
        
        def _do_toggle():
            try:
                parts = full_name.split('/')
                if len(parts) != 2:
                    self._append_diag(f"🔒 Toggle Privacy: Invalid repo format: {full_name}")
                    return
                
                owner, repo_name = parts
                
                url = f"https://api.github.com/repos/{owner}/{repo_name}"
                headers = {
                    "User-Agent": "GithubTool/2.0.2",
                    "Authorization": f"token {token}",
                    "Content-Type": "application/json"
                }
                
                data = json.dumps({"private": new_state}).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers=headers, method='PATCH')
                
                with urllib.request.urlopen(req, timeout=15) as resp:
                    result = json.loads(resp.read().decode('utf-8'))
                    actual_state = "Private" if result.get("private", False) else "Public"
                    
                    self._append_diag(f"🔒 Privacy changed: {full_name}")
                    self._append_diag(f"   {old_label} → {actual_state} ✅")
                    
                    # Update local data
                    repo["private"] = new_state
            
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    self._append_diag(f"🔒 Toggle Privacy DENIED: Token lacks permission for {full_name}")
                elif e.code == 404:
                    self._append_diag(f"🔒 Toggle Privacy: Repository {full_name} not found")
                else:
                    self._append_diag(f"🔒 Toggle Privacy FAILED: HTTP {e.code} - {e.reason}")
            except Exception as e:
                self._append_diag(f"🔒 Toggle Privacy FAILED: {e}")
        
        threading.Thread(target=_do_toggle, daemon=True).start()
    
    def fork_repo_async(self) -> None:
        """Fork a repo - runs on background thread."""
        repo = self._get_current_repo_from_active_tab()
        if not repo:
            self._append_diag("🔀 Fork: No repository selected")
            return
        
        token, _ = get_token()
        if not token:
            self._append_diag("🔀 Fork: No token available")
            return
        
        full_name = repo.get("full_name", "")
        
        # Confirm on main thread
        confirm = messagebox.askyesno(
            "Fork Repository",
            f"Fork this repository to your account?\n\n"
            f"📦 {full_name}\n\n"
            f"This will create a copy under your account."
        )
        
        if not confirm:
            self._append_diag(f"🔀 Fork: Cancelled for {full_name}")
            return
        
        def _do_fork():
            try:
                parts = full_name.split('/')
                if len(parts) != 2:
                    self._append_diag(f"🔀 Fork: Invalid repo format: {full_name}")
                    return
                
                owner, repo_name = parts
                
                self._append_diag(f"🔀 Forking {full_name}...")
                
                url = f"https://api.github.com/repos/{owner}/{repo_name}/forks"
                headers = {
                    "User-Agent": "GithubTool/2.0.2",
                    "Authorization": f"token {token}",
                    "Content-Type": "application/json"
                }
                
                req = urllib.request.Request(url, data=b'{}', headers=headers, method='POST')
                
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read().decode('utf-8'))
                    fork_name = result.get("full_name", "")
                    fork_url = result.get("html_url", "")
                    
                    self._append_diag(f"🔀 Fork successful!")
                    self._append_diag(f"   Original: {full_name}")
                    self._append_diag(f"   Fork:     {fork_name}")
                    self._append_diag(f"   URL:      {fork_url}")
            
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    self._append_diag(f"🔀 Fork DENIED: Token lacks permission")
                elif e.code == 404:
                    self._append_diag(f"🔀 Fork: Repository {full_name} not found")
                elif e.code == 422:
                    self._append_diag(f"🔀 Fork: You may already have a fork of {full_name}")
                else:
                    self._append_diag(f"🔀 Fork FAILED: HTTP {e.code} - {e.reason}")
            except Exception as e:
                self._append_diag(f"🔀 Fork FAILED: {e}")
        
        threading.Thread(target=_do_fork, daemon=True).start()
    
    def rename_repo_async(self) -> None:
        """Rename a repo - dialog on main thread, rename on background thread."""
        repo = self._get_current_repo_from_active_tab()
        if not repo:
            self._append_diag("✏️ Rename: No repository selected")
            return
        
        token, _ = get_token()
        if not token:
            self._append_diag("✏️ Rename: No token available")
            return
        
        full_name = repo.get("full_name", "")
        old_name = repo.get("name", "")
        
        # Ask for new name on MAIN THREAD
        new_name = simpledialog.askstring(
            "Rename Repository",
            f"Current name: {old_name}\n\n"
            f"Enter new name:",
            initialvalue=old_name
        )
        
        if not new_name or new_name.strip() == old_name:
            self._append_diag(f"✏️ Rename: Cancelled for {full_name}")
            return
        
        new_name = new_name.strip()
        
        # Strip .git if user added it
        if new_name.endswith('.git'):
            new_name = new_name[:-4]
        
        # Confirm
        confirm = messagebox.askyesno(
            "Confirm Rename",
            f"Rename repository?\n\n"
            f"📦 Current: {old_name}\n"
            f"✏️ New: {new_name}\n\n"
            f"⚠️ This will change the repository URL!\n"
            f"GitHub will redirect the old URL for a while,\n"
            f"but update your bookmarks and clones."
        )
        
        if not confirm:
            self._append_diag(f"✏️ Rename: Cancelled for {full_name}")
            return
        
        def _do_rename():
            try:
                parts = full_name.split('/')
                if len(parts) != 2:
                    self._append_diag(f"✏️ Rename: Invalid repo format: {full_name}")
                    return
                
                owner, repo_name = parts
                
                self._append_diag(f"✏️ Renaming {full_name} → {new_name}...")
                
                url = f"https://api.github.com/repos/{owner}/{repo_name}"
                headers = {
                    "User-Agent": "GithubTool/2.0.2",
                    "Authorization": f"token {token}",
                    "Content-Type": "application/json"
                }
                
                data = json.dumps({"name": new_name}).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers=headers, method='PATCH')
                
                with urllib.request.urlopen(req, timeout=15) as resp:
                    result = json.loads(resp.read().decode('utf-8'))
                    new_full_name = result.get("full_name", "")
                    new_url = result.get("html_url", "")
                    
                    self._append_diag(f"✏️ Rename successful!")
                    self._append_diag(f"   Old: {full_name}")
                    self._append_diag(f"   New: {new_full_name}")
                    self._append_diag(f"   URL: {new_url}")
                    
                    # Update local data
                    repo["name"] = new_name
                    repo["full_name"] = new_full_name
                    repo["html_url"] = new_url
            
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    self._append_diag(f"✏️ Rename DENIED: Token lacks permission for {full_name}")
                elif e.code == 404:
                    self._append_diag(f"✏️ Rename: Repository {full_name} not found")
                elif e.code == 422:
                    self._append_diag(f"✏️ Rename FAILED: Name '{new_name}' may already exist")
                else:
                    self._append_diag(f"✏️ Rename FAILED: HTTP {e.code} - {e.reason}")
            except Exception as e:
                self._append_diag(f"✏️ Rename FAILED: {e}")
        
        threading.Thread(target=_do_rename, daemon=True).start()

    # ========================================================================
    # SECTION: Search & Export Methods
    # ========================================================================
    def apply_search_filter(self) -> None:
        q = (self.search_var.get() or "").strip().lower()
        f = (self.filter_var.get() or "All").lower()
        tab = self.tab_control.index(self.tab_control.select())
        if tab == 1:
            source = self.repos_my
            table = self.table_my
        elif tab == 2:
            source = self.repos_orgs
            table = self.table_orgs
        elif tab == 3:
            source = self.repos_starred
            table = self.table_starred
        else:
            return
        def match(r: Dict) -> bool:
            name = (r.get("name") or "").lower()
            full = (r.get("full_name") or "").lower()
            if q and q not in name and q not in full:
                return False
            if f == "public" and r.get("private"):
                return False
            if f == "private" and not r.get("private"):
                return False
            if f == "forks" and not r.get("fork"):
                return False
            return True
        filtered = [r for r in source if match(r)]
        table.populate(filtered)

    def export_current_view_async(self) -> None:
        threading.Thread(target=self.export_current_view, daemon=True).start()

    def export_current_view(self) -> None:
        try:
            tab = self.tab_control.index(self.tab_control.select())
            if tab == 0:
                messagebox.showinfo("Export", "Welcome tab cannot be exported.")
                return
            elif tab == 1:
                data = self.repos_my
                tab_name = "My Repos"
            elif tab == 2:
                data = self.repos_orgs
                tab_name = "Org Repos"
            elif tab == 3:
                data = self.repos_starred
                tab_name = "Starred"
            elif tab == 4:
                data = self.tab_download_others.get_all_repos_for_export()
                tab_name = "Download From Others"
            elif tab == 5:
                messagebox.showinfo("Export", "Creation Lab cannot be exported.")
                return
            else:
                messagebox.showinfo("Export", "This tab doesn't support export.")
                return
            if not data:
                messagebox.showwarning("Export", f"No repositories to export from {tab_name}.")
                return
            fmt = self.export_format_var.get()
            if fmt == "csv":
                filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
                default_ext = ".csv"
            else:
                filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
                default_ext = ".txt"
            out = filedialog.asksaveasfilename(title=f"Export {tab_name} as {fmt.upper()}", defaultextension=default_ext, filetypes=filetypes)
            if not out:
                return
            if fmt == "csv":
                ExportManager.export_to_csv(data, out)
            else:
                ExportManager.export_to_txt(data, out)
            self._append_diag(f"Exported {len(data)} repos from '{tab_name}' to {out} ({fmt.upper()})")
            messagebox.showinfo("Export Complete", f"Exported {len(data)} repositories to:\n{out}")
        except Exception as e:
            self._append_diag(f"Export failed: {e}")
            messagebox.showerror("Export Failed", f"Export failed: {e}")


# ============================================================================
# MODULE: Main Entry Point
# ============================================================================
def main():
    """Main entry point for the application."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

# ============================================================================
# END OF FILE - gui.py
# GithubTool v2.0.2 - Console is King! 🎯
# (c) kindle15 / 2026
# ============================================================================