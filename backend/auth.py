import hashlib
import os
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from backend import models


def hash_password(password: str) -> str:
    """Hashes password securely using PBKDF2-HMAC-SHA256."""
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"{salt.hex()}${pwd_hash.hex()}"


def verify_password(stored_password_hash: str, provided_password: str) -> bool:
    """Verifies a password against the stored salt:hash string."""
    try:
        salt_hex, pwd_hash_hex = stored_password_hash.split('$')
        salt = bytes.fromhex(salt_hex)
        pwd_hash = bytes.fromhex(pwd_hash_hex)
        new_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return new_hash == pwd_hash
    except Exception:
        return False


def get_current_user(request: Request, db: Session) -> models.User | None:
    """Retrieves current logged in user from session cookies."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user


def require_login(request: Request, db: Session) -> models.User:
    """Requires user to be logged in; raises 401 if unauthenticated."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login to access this feature."
        )
    return user
