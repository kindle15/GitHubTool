#!/usr/bin/env python3
"""
repo_create_core.py - create & upload flow (uses centralized auth_token and network_utils)
"""
from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Callable, Tuple
import re
import requests

from auth_token import get_token
from network_utils import retry_requests, parse_oauth_scopes_from_headers

LogCallback = Optional[Callable[[str], None]]
ProgressCallback = Optional[Callable[[int, str], None]]

def _run(cmd: list[str], cwd: Optional[str] = None, log_cb: LogCallback = None) -> Tuple[int, str, str]:
    try:
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = proc.communicate()
        rc = proc.returncode
        if log_cb:
            if out:
                log_cb(out.strip())
            if err:
                log_cb(err.strip())
        return rc, out or "", err or ""
    except Exception as e:
        if log_cb:
            log_cb(f"Exception running {' '.join(cmd)}: {e}")
        return 1, "", str(e)

def create_local_copy(src: str, dest: str, log_cb: LogCallback = None) -> None:
    src_p = Path(src)
    dest_p = Path(dest)
    if not src_p.exists():
        raise FileNotFoundError(f"Source path not found: {src}")
    if dest_p.exists():
        raise FileExistsError(f"Destination already exists: {dest}")
    if log_cb:
        log_cb(f"Copying project from {src} to {dest} ...")
    shutil.copytree(src_p, dest_p)
    if log_cb:
        log_cb("Copy complete.")

def git_init(path: str, log_cb: LogCallback = None) -> None:
    if log_cb:
        log_cb("Initializing git repository...")
    rc, _, _ = _run(["git", "init"], cwd=path, log_cb=log_cb)
    if rc != 0:
        raise RuntimeError("git init failed")

def git_add_commit(path: str, message: str = "Initial commit", log_cb: LogCallback = None) -> None:
    if log_cb:
        log_cb("Adding files to git and committing...")
    rc, _, _ = _run(["git", "add", "."], cwd=path, log_cb=log_cb)
    if rc != 0:
        raise RuntimeError("git add failed")
    rc, _, _ = _run(["git", "commit", "-m", message], cwd=path, log_cb=log_cb)
    if rc != 0:
        _run(["git", "config", "user.email", "you@example.com"], cwd=path, log_cb=log_cb)
        _run(["git", "config", "user.name", "Your Name"], cwd=path, log_cb=log_cb)
        rc2, _, _ = _run(["git", "commit", "-m", message], cwd=path, log_cb=log_cb)
        if rc2 != 0:
            raise RuntimeError("git commit failed")

def git_set_remote(path: str, remote_url: str, log_cb: LogCallback = None) -> None:
    if log_cb:
        log_cb(f"Setting remote origin to {remote_url}")
    rc, _, _ = _run(["git", "remote", "add", "origin", remote_url], cwd=path, log_cb=log_cb)
    if rc != 0:
        rc2, _, _ = _run(["git", "remote", "set-url", "origin", remote_url], cwd=path, log_cb=log_cb)
        if rc2 != 0:
            raise RuntimeError("git remote add/set-url failed")

def git_push(path: str, branch: str = "main", log_cb: LogCallback = None) -> None:
    if log_cb:
        log_cb(f"Pushing to remote branch {branch} ...")
    rc, _, _ = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path, log_cb=log_cb)
    if rc != 0:
        _run(["git", "checkout", "-b", branch], cwd=path, log_cb=log_cb)
    else:
        _run(["git", "branch", "-M", branch], cwd=path, log_cb=log_cb)
    rc, out, err = _run(["git", "push", "-u", "origin", branch], cwd=path, log_cb=log_cb)
    if rc != 0:
        raise RuntimeError(f"git push failed. Check remote permissions and credentials. Details: {err or out}")

def _gh_available() -> bool:
    return shutil.which("gh") is not None

@retry_requests(retries=3, backoff=0.5)
def _requests_get_with_retry(url, headers, timeout=10):
    return requests.get(url, headers=headers, timeout=timeout)

@retry_requests(retries=3, backoff=0.5)
def _requests_post_with_retry(url, headers, json_payload, timeout=30):
    return requests.post(url, headers=headers, json=json_payload, timeout=timeout)

def _get_token_user(token: str, log_cb: LogCallback = None) -> Optional[str]:
    if not token:
        return None
    try:
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        r = _requests_get_with_retry("https://api.github.com/user", headers=headers, timeout=10)
        if r.status_code == 200:
            scopes = parse_oauth_scopes_from_headers(r.headers)
            if log_cb:
                log_cb(f"Token scopes: {scopes or '(none)'}")
            return r.json().get("login")
        if log_cb:
            log_cb(f"Token user lookup failed: {r.status_code} {r.text}")
    except Exception as e:
        if log_cb:
            log_cb(f"Token user lookup exception: {e}")
    return None

def _owner_from_clone_url(clone_url: str) -> Optional[str]:
    if not clone_url:
        return None
    m = re.match(r"https?://[^/]+/([^/]+)/[^/]+(?:\.git)?", clone_url)
    if m:
        return m.group(1)
    m2 = re.match(r"git@[^:]+:([^/]+)/[^/]+(?:\.git)?", clone_url)
    if m2:
        return m2.group(1)
    return None

def github_create_repo_via_gh(name: str, private: bool, description: str, path: Optional[str], log_cb: LogCallback = None) -> str:
    cmd = ["gh", "repo", "create", name, "--confirm", "--source", path or ".", "--remote", "origin", "--push"]
    if private:
        cmd.append("--private")
    if description:
        cmd.extend(["--description", description])
    if log_cb:
        log_cb("Creating GitHub repo via gh CLI (with push)...")
    rc, out, err = _run(cmd, cwd=path, log_cb=log_cb)
    if rc != 0:
        raise RuntimeError(f"gh repo create failed: {err or out}")
    rc2, out2, _ = _run(["git", "remote", "get-url", "origin"], cwd=path, log_cb=log_cb)
    if rc2 != 0:
        raise RuntimeError("Failed to read remote URL after gh create")
    return out2.strip()

def github_create_repo_via_api(name: str, private: bool, description: str, token: str, org: Optional[str], log_cb: LogCallback = None) -> str:
    if not token:
        raise RuntimeError("GitHub token required for API repo creation")
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    if org:
        url = f"https://api.github.com/orgs/{org}/repos"
    else:
        url = "https://api.github.com/user/repos"
    payload = {"name": name, "private": bool(private), "description": description or ""}
    if log_cb:
        log_cb(f"Creating GitHub repo via REST API at {url} ...")
    resp = _requests_post_with_retry(url, headers=headers, json_payload=payload, timeout=30)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"GitHub API create repo failed: {resp.status_code} {resp.text}")
    data = resp.json()
    clone_url = data.get("clone_url") or data.get("ssh_url")
    if not clone_url:
        raise RuntimeError("No clone URL returned from GitHub API")
    return clone_url

def run_full_repo_creation_flow(src_folder: str,
                                dest_folder: str,
                                repo_name: Optional[str] = None,
                                private: bool = True,
                                description: str = "",
                                branch: str = "main",
                                commit_message: str = "Initial commit",
                                org: Optional[str] = None,
                                no_usb: bool = False,
                                log_cb: LogCallback = None,
                                progress_cb: ProgressCallback = None):
    if progress_cb:
        progress_cb(0, "Starting repo creation flow")
    src = Path(src_folder).resolve()
    dest = Path(dest_folder).resolve()
    if not src.exists():
        raise FileNotFoundError("Source folder does not exist")
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError("Destination folder exists and is not empty")
    if src != dest:
        create_local_copy(str(src), str(dest), log_cb=log_cb)
    else:
        if log_cb:
            log_cb("Source and destination are the same; using existing folder")
    if progress_cb:
        progress_cb(10, "Local copy ready")

    git_init(str(dest), log_cb=log_cb)
    if progress_cb:
        progress_cb(25, "Git initialized")
    git_add_commit(str(dest), message=commit_message, log_cb=log_cb)
    if progress_cb:
        progress_cb(45, "Committed initial files")

    name = repo_name or dest.name

    token = get_token(no_usb=no_usb, log_cb=log_cb)
    token_user = _get_token_user(token, log_cb=log_cb) if token else None
    if progress_cb:
        progress_cb(55, "Token checked")

    remote_url = None
    if _gh_available():
        try:
            remote_url = github_create_repo_via_gh(name=name, private=private, description=description, path=str(dest), log_cb=log_cb)
            if progress_cb:
                progress_cb(65, "Remote created via gh")
        except Exception as e:
            if log_cb:
                log_cb(f"gh create failed, falling back to API: {e}")
            remote_url = None

    if not remote_url:
        remote_url = github_create_repo_via_api(name=name, private=private, description=description, token=token, org=org, log_cb=log_cb)
        if progress_cb:
            progress_cb(75, "Remote created via API")

    owner = _owner_from_clone_url(remote_url)
    if log_cb:
        log_cb(f"Remote owner parsed as: {owner}")
    if org:
        if owner and owner.lower() != org.lower():
            raise RuntimeError(f"Created remote owner '{owner}' does not match requested org '{org}'")
    else:
        if token_user:
            if owner and owner.lower() != token_user.lower():
                raise RuntimeError(f"Remote owner '{owner}' is not the authenticated user '{token_user}'. Upload aborted.")
        else:
            if log_cb:
                log_cb("Warning: token user unknown; cannot verify ownership. If this was created by gh interactive auth, ensure you have rights to push.")

    git_set_remote(str(dest), remote_url, log_cb=log_cb)
    if progress_cb:
        progress_cb(85, "Remote set")
    try:
        git_push(str(dest), branch=branch, log_cb=log_cb)
    except Exception as e:
        raise RuntimeError(f"Upload (git push) failed: {e}")
    if progress_cb:
        progress_cb(100, "Push complete")
    if log_cb:
        log_cb(f"Repository created and pushed: {remote_url}")
    return remote_url
