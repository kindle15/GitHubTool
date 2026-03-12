"""
download_core.py
Functions to fetch repositories from the GitHub API using a personal access token.
Uses urllib.request to avoid extra dependencies and supports pagination.
"""

import urllib.request
import json
import time
from typing import List, Dict, Tuple

DEFAULT_PER_PAGE = 100
REQUEST_TIMEOUT = 10  # seconds

class GitHubFetchError(Exception):
    pass

def _request_json(url: str, headers: dict, timeout: int = REQUEST_TIMEOUT) -> Tuple[object, dict]:
    """
    Perform a single HTTP GET and return (parsed_json, response_headers_dict).
    Raises GitHubFetchError on HTTP errors or parse errors.
    """
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            text = raw.decode('utf-8', errors='replace')
            data = json.loads(text)
            # normalize headers to a dict
            hdrs = {k: v for k, v in resp.getheaders()}
            return data, hdrs
    except urllib.error.HTTPError as e:
        # include body if available for diagnostics
        try:
            body = e.read().decode('utf-8', errors='ignore')
        except Exception:
            body = ""
        raise GitHubFetchError(f"HTTP {e.code} {e.reason}: {body}") from e
    except Exception as e:
        raise GitHubFetchError(f"Request failed: {e}") from e

def fetch_user_repos(token: str, per_page: int = DEFAULT_PER_PAGE) -> List[Dict]:
    """
    Fetch all repositories for the authenticated user using the provided token.
    Returns a list of repo dicts (as returned by the GitHub API).
    Raises GitHubFetchError on failure.
    """
    if not token:
        raise GitHubFetchError("No token provided")

    headers = {"Authorization": f"token {token}", "User-Agent": "GithubTool/1.0"}
    repos = []
    page = 1

    while True:
        url = f"https://api.github.com/user/repos?per_page={per_page}&page={page}"
        data, hdrs = _request_json(url, headers)
        if not isinstance(data, list):
            # sometimes API returns a dict with message on error
            raise GitHubFetchError(f"Unexpected response: {data}")
        repos.extend(data)
        link = hdrs.get("Link", "")
        if 'rel="next"' not in link:
            break
        page += 1
        # small delay to be polite
        time.sleep(0.1)

    return repos
