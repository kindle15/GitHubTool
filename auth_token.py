# auth_token.py - robust loader compatible with repos_csv.py behavior
import os
import ctypes

TOKEN_FILENAME = "PersonalAccessToken.txt"
MIN_TOKEN_LENGTH = 20
_DRIVE_REMOVABLE = 2
_DRIVE_FIXED = 3

def _drive_type_name(dtype):
    return {
        0: "DRIVE_UNKNOWN",
        1: "DRIVE_NO_ROOT_DIR",
        2: "DRIVE_REMOVABLE",
        3: "DRIVE_FIXED",
        4: "DRIVE_REMOTE",
        5: "DRIVE_CDROM",
        6: "DRIVE_RAMDISK",
    }.get(dtype, str(dtype))

def _scan_d_to_z_accept_fixed(min_length=MIN_TOKEN_LENGTH):
    scanned = []
    for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
        root = f"{letter}:\\"
        if not os.path.exists(root):
            scanned.append((root, "no-drive"))
            continue
        try:
            dtype = ctypes.windll.kernel32.GetDriveTypeW(root)
        except Exception as e:
            scanned.append((root, f"drive-type-error:{e}"))
            continue
        # Accept removable or fixed drives (covers USBs that report as fixed)
        if dtype not in (_DRIVE_REMOVABLE, _DRIVE_FIXED):
            scanned.append((root, f"drive-type-not-accepted:{_drive_type_name(dtype)}"))
            continue
        path = os.path.join(root, TOKEN_FILENAME)
        if not os.path.isfile(path):
            scanned.append((path, "missing"))
            continue
        try:
            with open(path, "rb") as f:
                raw = f.read()
        except Exception as e:
            scanned.append((path, f"read-error:{e}"))
            continue
        try:
            token = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            token = raw.decode("latin-1", errors="replace")
        token_clean = token.strip()
        if len(token_clean) < min_length:
            scanned.append((path, f"invalid-length:{len(token_clean)}"))
            continue
        masked = token_clean[:6] + "..." + token_clean[-4:] if len(token_clean) > 12 else token_clean
        source = f"USB {letter}:\\ (found {TOKEN_FILENAME}, masked {masked})"
        return token_clean, source
    summary = "No token found on D:–Z:. Scanned: " + "; ".join(f"{p}->{s}" for p, s in scanned)
    return None, summary

def get_token(min_length=MIN_TOKEN_LENGTH):
    try:
        token, source = _scan_d_to_z_accept_fixed(min_length=min_length)
        if token:
            return token, source
    except Exception as e:
        return None, f"Error scanning drives: {e}"
    env_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if env_token:
        t = env_token.strip()
        if len(t) >= min_length:
            masked = t[:6] + "..." + t[-4:] if len(t) > 12 else t
            return t, f"Environment variable (masked {masked})"
        return None, f"Environment token present but too short (len={len(t)})"
    return None, "No token found (D:–Z: and GITHUB_TOKEN checked)"
