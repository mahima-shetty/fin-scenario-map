"""
AES-256-GCM encryption at rest for sensitive fields (PRD FR9).
When DATA_ENCRYPTION_KEY is set (base64-encoded 32 bytes), values are stored with prefix "AES:"
so we can detect and decrypt on read. If key is missing, no encryption is applied (backward compatible).
"""
import base64
import os

_ENC_PREFIX = "AES:"


def _get_key() -> bytes | None:
    """Return 32-byte key from settings or None if not configured."""
    try:
        from .settings import get_settings
        raw = (get_settings().data_encryption_key or "").strip()
    except Exception:
        raw = ""
    if not raw or len(raw) < 32:
        return None
    try:
        key = base64.b64decode(raw)
        if len(key) == 32:
            return key
    except Exception:
        pass
    return None


def encrypt_value(plaintext: str) -> str:
    """Encrypt plaintext with AES-256-GCM. Returns 'AES:' + base64(nonce||ciphertext||tag). No-op if key not set."""
    key = _get_key()
    if not key or not plaintext:
        return plaintext or ""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        nonce = os.urandom(12)
        aes = AESGCM(key)
        ct = aes.encrypt(nonce, plaintext.encode("utf-8"), None)
        return _ENC_PREFIX + base64.b64encode(nonce + ct).decode("ascii")
    except Exception:
        return plaintext


def decrypt_value(ciphertext: str) -> str:
    """Decrypt if value has 'AES:' prefix; otherwise return as-is."""
    if not ciphertext or not ciphertext.startswith(_ENC_PREFIX):
        return ciphertext or ""
    key = _get_key()
    if not key:
        return ciphertext
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        raw = base64.b64decode(ciphertext[len(_ENC_PREFIX):])
        nonce, ct = raw[:12], raw[12:]
        aes = AESGCM(key)
        return aes.decrypt(nonce, ct, None).decode("utf-8")
    except Exception:
        return ciphertext
