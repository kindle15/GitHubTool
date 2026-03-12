# auth_token_compat.py - compatibility shim forwarding legacy names to auth_token.get_token
from typing import Tuple, Optional
try:
    from auth_token import get_token
except Exception as e:
    def get_token(min_length: int = 20) -> Tuple[Optional[str], str]:
        return None, f"auth_token.get_token unavailable: {e}"

def _forward_get_token(min_length: int = 20):
    return get_token(min_length=min_length)

def load_token_from_removable_drives(min_length: int = 20):
    return _forward_get_token(min_length=min_length)

def load_token_from_removable_or_fixed_d_to_z(min_length: int = 20):
    return _forward_get_token(min_length=min_length)

def load_token_from_usb_d_to_z(min_length: int = 20):
    return _forward_get_token(min_length=min_length)

def load_token_from_usb(min_length: int = 20):
    return _forward_get_token(min_length=min_length)

__all__ = [
    "get_token",
    "load_token_from_removable_drives",
    "load_token_from_removable_or_fixed_d_to_z",
    "load_token_from_usb_d_to_z",
    "load_token_from_usb",
]
