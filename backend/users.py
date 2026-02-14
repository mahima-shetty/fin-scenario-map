from passlib.context import CryptContext


# Demo users (email -> password) for development
demo_users = {
    "test@example.com": "password123",
    "alice@example.com": "alicepass"
}

def verify_user(email: str, password: str) -> bool:
    """Return True if user exists and password matches"""
    return email in demo_users and demo_users[email] == password