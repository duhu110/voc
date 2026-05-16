from __future__ import annotations

import hashlib
import hmac
import os
import re


def parse_auth_users(raw_value: str | None = None) -> dict[str, str]:
    """Parse VOC_CHAINLIT_AUTH_USERS into a username -> password spec mapping."""
    raw = raw_value if raw_value is not None else os.getenv("VOC_CHAINLIT_AUTH_USERS", "")
    users: dict[str, str] = {}
    for item in re.split(r"[;,]\s*", raw.strip()):
        if not item or ":" not in item:
            continue
        username, password_spec = item.split(":", 1)
        username = username.strip()
        password_spec = password_spec.strip()
        if username and password_spec:
            users[username] = password_spec
    return users


def verify_password(password: str, password_spec: str) -> bool:
    """Verify a password against a plain or sha256 password spec."""
    if password_spec.startswith("sha256:"):
        expected = password_spec.removeprefix("sha256:").strip().lower()
        actual = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(actual, expected)
    return hmac.compare_digest(password, password_spec)


def is_valid_user(username: str, password: str) -> bool:
    password_spec = parse_auth_users().get(username)
    if not password_spec:
        return False
    return verify_password(password, password_spec)
