import bcrypt
import json
import os
import tempfile
import time

from filelock import FileLock
from flask import current_app

from config.settings import ADMIN_PASSWORD_HASH, MAX_LOGIN_ATTEMPTS, LOGIN_LOCKOUT_MINUTES


def verify_password(password: str) -> bool:
    stored_hash = ADMIN_PASSWORD_HASH.encode()
    return bcrypt.checkpw(password.encode(), stored_hash)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# ============================================================
# Lockout state — file-based, shared across gunicorn workers.
# Struktur: {ip: {"count": int, "first_attempt": float}}
# Override lokasi file via env AUTH_STATE_FILE (untuk disk persisten).
# ============================================================

def _state_path():
    override = os.environ.get("AUTH_STATE_FILE")
    path = override or os.path.join(current_app.instance_path, "auth_state.json")
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    return path


def _load_state(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_state(path, data):
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path) or ".")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _purge_expired(state):
    now = time.time()
    lockout_seconds = LOGIN_LOCKOUT_MINUTES * 60
    return {
        ip: attempt
        for ip, attempt in state.items()
        if now - attempt.get("first_attempt", 0) < lockout_seconds
    }


def check_lockout(ip: str) -> tuple[bool, int]:
    """Check if IP is locked out. Returns (is_locked, seconds_remaining)."""
    path = _state_path()
    with FileLock(path + ".lock", timeout=10):
        state = _load_state(path)
        attempt = state.get(ip)
        if not attempt:
            return False, 0

        elapsed = time.time() - attempt["first_attempt"]
        lockout_seconds = LOGIN_LOCKOUT_MINUTES * 60

        if elapsed >= lockout_seconds:
            state.pop(ip, None)
            _save_state(path, state)
            return False, 0

        if attempt["count"] >= MAX_LOGIN_ATTEMPTS:
            remaining = int(lockout_seconds - elapsed)
            return True, remaining

        return False, 0


def record_failed_attempt(ip: str):
    path = _state_path()
    with FileLock(path + ".lock", timeout=10):
        state = _purge_expired(_load_state(path))
        attempt = state.get(ip)
        if not attempt:
            attempt = {"count": 0, "first_attempt": time.time()}
            state[ip] = attempt
        attempt["count"] += 1
        _save_state(path, state)


def clear_attempts(ip: str):
    path = _state_path()
    with FileLock(path + ".lock", timeout=10):
        state = _load_state(path)
        if ip in state:
            state.pop(ip)
            _save_state(path, state)
