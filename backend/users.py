"""User store and roles for JWT + RBAC. Demo users only (email -> {password, role})."""
from typing import Literal

Role = Literal["user", "admin"]

# Demo users: email -> {password, role}
demo_users: dict[str, dict[str, str]] = {
    "test@example.com": {"password": "password123", "role": "user"},
    "alice@example.com": {"password": "alicepass", "role": "user"},
    "admin@example.com": {"password": "adminpass", "role": "admin"},
}


def verify_user(email: str, password: str) -> bool:
    """Return True if user exists and password matches."""
    if email not in demo_users:
        return False
    return demo_users[email]["password"] == password


def get_user_role(email: str) -> Role:
    """Return role for email; default 'user' if unknown."""
    if email not in demo_users:
        return "user"
    r = demo_users[email].get("role") or "user"
    return r if r in ("user", "admin") else "user"