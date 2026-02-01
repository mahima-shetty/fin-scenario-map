from passlib.context import CryptContext


# Mock users dictionary (email -> hashed password)
mock_users = {
    "test@example.com": "password123",
    "alice@example.com": "alicepass"
}

def verify_user(email: str, password: str) -> bool:
    """Return True if user exists and password matches"""
    return email in mock_users and mock_users[email] == password