from __future__ import annotations

import hashlib

from chainlit_app.auth import parse_auth_users, verify_password


def test_parse_auth_users_supports_commas_and_semicolons() -> None:
    users = parse_auth_users("alice:secret,bob:sha256:abc; carol: pass ")

    assert users == {
        "alice": "secret",
        "bob": "sha256:abc",
        "carol": "pass",
    }


def test_verify_plain_password() -> None:
    assert verify_password("secret", "secret")
    assert not verify_password("wrong", "secret")


def test_verify_sha256_password() -> None:
    digest = hashlib.sha256("secret".encode("utf-8")).hexdigest()

    assert verify_password("secret", f"sha256:{digest}")
    assert not verify_password("wrong", f"sha256:{digest}")
