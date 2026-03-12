# bootstrap_auth_token.py
import os, re, sys, shutil

AUTH_TOKEN_CONTENT = r'''# auth_token.py - robust loader compatible with repos_csv.py behavior
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
'''

COMPAT_CONTENT = r'''# auth_token_compat.py - compatibility shim forwarding legacy names to auth_token.get_token
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
'''

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"WROTE {path}")

def patch_imports(root):
    # Replace common legacy imports with canonical get_token import
    patterns = [
        (r'from\s+auth_token\s+import\s+load_token_from_removable_drives', 'from auth_token import get_token'),
        (r'from\s+auth_token\s+import\s+load_token_from_removable_or_fixed_d_to_z', 'from auth_token import get_token'),
        (r'from\s+auth_token\s+import\s+load_token_from_usb_d_to_z', 'from auth_token import get_token'),
        (r'from\s+auth_token\s+import\s+load_token_from_usb', 'from auth_token import get_token'),
    ]
    changed_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # skip virtualenv and .git directories
        if any(part in ('.git','venv','env','__pycache__') for part in dirpath.split(os.sep)):
            continue
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            p = os.path.join(dirpath, fn)
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            new_text = text
            for pat, repl in patterns:
                new_text = re.sub(pat, repl, new_text)
            if new_text != text:
                backup = p + ".bak"
                shutil.copy2(p, backup)
                with open(p, "w", encoding="utf-8") as f:
                    f.write(new_text)
                changed_files.append(p)
    return changed_files

def main():
    root = os.getcwd()
    auth_path = os.path.join(root, "auth_token.py")
    compat_path = os.path.join(root, "auth_token_compat.py")

    if os.path.exists(auth_path):
        print("NOTE auth_token.py already exists at", auth_path)
    else:
        write_file(auth_path, AUTH_TOKEN_CONTENT)

    if os.path.exists(compat_path):
        print("NOTE auth_token_compat.py already exists at", compat_path)
    else:
        write_file(compat_path, COMPAT_CONTENT)

    print("\nPatching imports to use canonical get_token where possible...")
    changed = patch_imports(root)
    if changed:
        print("Patched files:")
        for c in changed:
            print("  ", c)
    else:
        print("No import replacements needed.")

    print("\nVerification attempt:")
    print("  Python executable:", sys.executable)
    print("  auth_token.py path:", auth_path)
    print("  auth_token_compat.py path:", compat_path)
    print("\nRun the GUI from this same environment now (python -m gui or python gui.py).")
    print("If you use a frozen EXE, rebuild it after these changes.")

if __name__ == '__main__':
    main()
