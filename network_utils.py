#!/usr/bin/env python3
"""
network_utils.py

Shared network helpers:
 - retry_requests decorator
 - parse_oauth_scopes_from_headers
 - parse_link_header (returns next URL or None)
"""
from __future__ import annotations
import time
from typing import Callable, Optional, Dict
import requests
from functools import wraps

def retry_requests(retries: int = 3, backoff: float = 0.5):
    """
    Decorator to retry a function that performs requests.* calls on RequestException.
    Retries with exponential backoff.
    """
    def deco(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, retries + 1):
                try:
                    return fn(*args, **kwargs)
                except requests.RequestException as e:
                    last_exc = e
                    if attempt == retries:
                        raise
                    time.sleep(backoff * (2 ** (attempt - 1)))
            if last_exc:
                raise last_exc
        return wrapper
    return deco


def parse_oauth_scopes_from_headers(headers: Optional[Dict[str, str]]) -> str:
    if not headers:
        return ""
    return headers.get("x-oauth-scopes") or headers.get("X-OAuth-Scopes") or ""


def parse_link_header(link_header: str) -> Optional[str]:
    """
    Parse a Link header and return the URL for rel="next" if present, else None.
    """
    if not link_header:
        return None
    parts = [p.strip() for p in link_header.split(",")]
    for part in parts:
        if ';' not in part:
            continue
        url_part, rel_part = part.split(";", 1)
        url_part = url_part.strip().strip("<>").strip()
        rel_part = rel_part.strip()
        if 'rel="next"' in rel_part:
            return url_part
    return None
