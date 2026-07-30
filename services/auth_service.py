import bcrypt
import os
import time
from config.settings import ADMIN_PASSWORD_HASH, MAX_LOGIN_ATTEMPTS, LOGIN_LOCKOUT_MINUTES

# In-memory lockout tracking (IP -> {"count": int, "first_attempt": float})
_login_attempts = {}


def verify_password(password: str) -> bool:
    stored_hash = ADMIN_PASSWORD_HASH.encode()
    return bcrypt.checkpw(password.encode(), stored_hash)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_lockout(ip: str) -> tuple[bool, int]:
    """Check if IP is locked out. Returns (is_locked, seconds_remaining)."""
    if ip not in _login_attempts:
        return False, 0

    attempt = _login_attempts[ip]
    elapsed = time.time() - attempt["first_attempt"]
    lockout_seconds = LOGIN_LOCKOUT_MINUTES * 60

    if elapsed >= lockout_seconds:
        del _login_attempts[ip]
        return False, 0

    if attempt["count"] >= MAX_LOGIN_ATTEMPTS:
        remaining = int(lockout_seconds - elapsed)
        return True, remaining

    return False, 0


def record_failed_attempt(ip: str):
    if ip not in _login_attempts:
        _login_attempts[ip] = {"count": 0, "first_attempt": time.time()}
    _login_attempts[ip]["count"] += 1


def clear_attempts(ip: str):
    _login_attempts.pop(ip, None)
