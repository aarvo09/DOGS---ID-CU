from datetime import datetime, timedelta, timezone
from typing import Optional, List
import bcrypt
import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db

security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False

def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticates an admin user by email and password, updating last_login if successful."""
    clean_email = email.strip().lower()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, email, password_hash, role, is_active, last_login, created_at
            FROM admin_users
            WHERE email = ?
        """, (clean_email,))
        user = cursor.fetchone()
        if not user or not verify_password(password, user["password_hash"]):
            return None
        if not user["is_active"]:
            return None
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE admin_users SET last_login = ? WHERE id = ?", (now_str, user["id"]))
        return dict(user)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decode and validate a signed JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def extract_token_from_request(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = None) -> Optional[str]:
    """Helper to extract JWT token from Bearer header or cookies safely."""
    if credentials and isinstance(credentials, HTTPAuthorizationCredentials) and credentials.credentials:
        return credentials.credentials
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1].strip()
    cookie_token = request.cookies.get("dogcu_access_token") or request.cookies.get("access_token")
    if cookie_token:
        return cookie_token.strip()
    return None

def get_current_admin(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """FastAPI dependency to extract and verify the current authenticated admin user via Bearer header or cookie."""
    token = extract_token_from_request(
        request, 
        credentials if isinstance(credentials, HTTPAuthorizationCredentials) else None
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, role, is_active, last_login FROM admin_users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account no longer exists.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This administrative account has been deactivated.",
            )
        return dict(user)

def get_optional_admin(
    request: Request,
) -> Optional[dict]:
    """Returns the authenticated admin if available, or None without raising an HTTPException."""
    try:
        token = extract_token_from_request(request)
        if not token:
            return None
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, role, is_active, last_login FROM admin_users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if not user or not user["is_active"]:
                return None
            return dict(user)
    except Exception:
        return None

def require_roles(allowed_roles: List[str]):
    """Role-based authorization dependency factory."""
    def role_checker(current_user: dict = Depends(get_current_admin)) -> dict:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {', '.join(allowed_roles)}",
            )
        return current_user
    return role_checker
