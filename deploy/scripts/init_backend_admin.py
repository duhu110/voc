from __future__ import annotations

import argparse
import secrets
import string

from sqlalchemy import text

from backend_api.auth import hash_password
from voc_agent.core.db import get_engine


def _default_password() -> str:
    alphabet = string.ascii_letters + string.digits + "-_"
    return "".join(secrets.choice(alphabet) for _ in range(24))


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or reset a backend admin user.")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default=None)
    parser.add_argument("--display-name", default="系统管理员")
    parser.add_argument(
        "--reset-existing",
        action="store_true",
        help="Reset password and reactivate the user when the username already exists.",
    )
    args = parser.parse_args()

    password = args.password or _default_password()
    password_hash = hash_password(password)

    with get_engine().begin() as conn:
        existing = conn.execute(
            text("select id, username from app_users where username = :username"),
            {"username": args.username},
        ).mappings().first()
        if existing and not args.reset_existing:
            print(f"Admin user already exists: username={args.username}")
            print("Use --reset-existing to reset its password.")
            return
        if existing:
            conn.execute(
                text(
                    """
                    update app_users
                    set display_name = :display_name,
                        password_hash = :password_hash,
                        role = 'admin',
                        status = 'active',
                        token_version = token_version + 1,
                        updated_at = now()
                    where username = :username
                    """
                ),
                {
                    "username": args.username,
                    "display_name": args.display_name,
                    "password_hash": password_hash,
                },
            )
            action = "reset"
        else:
            conn.execute(
                text(
                    """
                    insert into app_users (username, display_name, password_hash, role, status)
                    values (:username, :display_name, :password_hash, 'admin', 'active')
                    """
                ),
                {
                    "username": args.username,
                    "display_name": args.display_name,
                    "password_hash": password_hash,
                },
            )
            action = "created"

    print(f"Admin user {action}: username={args.username}")
    if args.password is None:
        print(f"Generated password: {password}")


if __name__ == "__main__":
    main()
