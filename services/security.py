"""
Security utilities: CSRF, rate limiting, security headers, safe error handling.
"""
import hashlib
import hmac
import os
import time
import secrets
from functools import wraps
from flask import request, session, abort, g


# ============================================================
# CSRF Protection
# ============================================================

def generate_csrf_token():
    """Generate or return existing CSRF token for the current session."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


def validate_csrf():
    """Validate CSRF token on POST requests. Call before processing."""
    if request.method == "POST":
        token = request.form.get("_csrf_token", "")
        expected = session.get("_csrf_token", "")
        if not token or not expected or not hmac.compare_digest(token, expected):
            abort(403, description="CSRF token tidak valid. Silakan refresh halaman.")


# ============================================================
# Rate Limiting (in-memory, per-IP)
# ============================================================

_rate_limits = {}  # ip -> {"endpoint": [(timestamp, ...)]}


def rate_limit(max_requests, window_seconds, key_func=None):
    """
    Decorator: limit requests per IP per time window.
    key_func(request) -> str for custom key (default: remote_addr).
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = get_real_ip()
            key = key_func(request) if key_func else ip
            cache_key = f"{f.__name__}:{key}"
            now = time.time()
            cutoff = now - window_seconds

            if cache_key not in _rate_limits:
                _rate_limits[cache_key] = []

            # Prune old entries
            _rate_limits[cache_key] = [
                t for t in _rate_limits[cache_key] if t > cutoff
            ]

            if len(_rate_limits[cache_key]) >= max_requests:
                abort(429, description="Terlalu banyak percobaan. Coba lagi nanti.")

            _rate_limits[cache_key].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================
# IP Address (handle reverse proxy)
# ============================================================

from config.settings import TRUSTED_PROXIES


def get_real_ip():
    """Get real client IP. Only trust X-Forwarded-For from known proxies."""
    remote = request.remote_addr or "unknown"
    if TRUSTED_PROXIES and remote in TRUSTED_PROXIES and request.headers.get("X-Forwarded-For"):
        # Only trust X-Forwarded-For if request comes from a known proxy
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    return request.remote_addr or "unknown"


# ============================================================
# Security Headers Middleware
# ============================================================

def add_security_headers(response):
    """Add security headers to every response."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # CSP: allow inline scripts (needed for our JS) + Google Fonts
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self'"
    )
    return response


# ============================================================
# Safe Error Messages
# ============================================================

def safe_error_message(e, context="operasi"):
    """Return generic error message, log the real error server-side."""
    import logging
    logging.error(f"Error during {context}: {e}", exc_info=True)
    return f"Terjadi kesalahan saat {context}. Silakan coba lagi atau hubungi admin."
