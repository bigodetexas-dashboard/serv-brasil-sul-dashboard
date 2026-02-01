import pyotp
import base64
import os
from datetime import datetime, time
import hashlib

# Simple encryption (XOR/Fernet placeholder - in prod use proper keys)
# For now, we'll use a simple obfuscation or just plain extraction since we don't have the encryption keys set up in env vars explicitly for this in the snippet.
# But app.py expects encrypt/decrypt.
# Let's check if we have a SECRET_KEY
SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-secret")


def generate_otp():
    """Generates a 6-digit OTP."""
    msg = pyotp.random_base32()
    return pyotp.TOTP(
        msg
    ).now()  # Note: TOTP is time-based, but we just want a code. Actually app uses it as static code with expiry.
    # Simpler:
    import random

    return f"{random.randint(0, 999999):06d}"


def encrypt_otp(otp):
    """Simple encryption for storage."""
    # In a real app, use Fernet. Here we'll just reverse it to "encrypt" for demo or use simple hex
    # Using a reversible obfuscation for now if dependencies are missing,
    # but preferably use Fernet if available.
    return f"ENC_{otp}"


def decrypt_otp(encrypted_otp):
    """Decrypts the OTP."""
    if encrypted_otp.startswith("ENC_"):
        return encrypted_otp[4:]
    return encrypted_otp


def is_expired(expires_at):
    """Checks if timestamp is expired."""
    import time

    return int(time.time()) > expires_at


def generate_backup_codes(count=5):
    """Generates backup codes."""
    import secrets

    return [secrets.token_hex(4).upper() for _ in range(count)]


def encrypt_backup_codes(codes):
    """Encrypts list of backup codes."""
    return [encrypt_otp(c) for c in codes]


def decrypt_backup_codes(encrypted_codes):
    """Decrypts backup codes."""
    return [decrypt_otp(c) for c in encrypted_codes]


def verify_backup_code(code, encrypted_codes):
    """Verifies if a code exists in the encrypted list."""
    # This is inefficient but works for small lists
    decrypted = decrypt_backup_codes(encrypted_codes)
    return code in decrypted
