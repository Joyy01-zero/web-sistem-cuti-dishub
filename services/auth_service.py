import time

import bcrypt

from config.settings import ADMIN_PASSWORD_HASH, LOGIN_LOCKOUT_MINUTES, MAX_LOGIN_ATTEMPTS
from services.sheets_service import get_auth_state, set_auth_state, delete_auth_state


def verify_password(password: str) -> bool:
    stored_hash = ADMIN_PASSWORD_HASH.encode()
    return bcrypt.checkpw(password.encode(), stored_hash)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# ============================================================
# Lockout state — Google Sheets based, persistent across restarts.
# ============================================================


def check_lockout(ip: str) -> tuple[bool, int]:
    """Check if IP is locked out. Returns (is_locked, seconds_remaining)."""
    attempt = get_auth_state(ip)
    if not attempt:
        return False, 0

    elapsed = time.time() - attempt["first_attempt"]
    lockout_seconds = LOGIN_LOCKOUT_MINUTES * 60

    # Expired — clean up
    if elapsed >= lockout_seconds:
        delete_auth_state(ip)
        return False, 0

    if attempt["count"] >= MAX_LOGIN_ATTEMPTS:
        remaining = int(lockout_seconds - elapsed)
        return True, remaining

    return False, 0


def record_failed_attempt(ip: str):
    attempt = get_auth_state(ip)
    if not attempt:
        set_auth_state(ip, 1, time.time())
    else:
        # Purge if expired
        elapsed = time.time() - attempt["first_attempt"]
        if elapsed >= LOGIN_LOCKOUT_MINUTES * 60:
            set_auth_state(ip, 1, time.time())
        else:
            set_auth_state(ip, attempt["count"] + 1, attempt["first_attempt"])


def clear_attempts(ip: str):
    delete_auth_state(ip)
