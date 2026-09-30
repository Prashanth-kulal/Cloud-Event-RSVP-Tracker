"""
Password hashing using bcrypt directly (cost factor 12).
Avoids passlib wrap-bug incompatibility on Python 3.12 while maintaining standard bcrypt hashes.
"""
import bcrypt


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    pwd_bytes = plain_password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored hash."""
    try:
        pwd_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False
