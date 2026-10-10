from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends, Response
from app.database import get_db
from app.models import LoginRequest, TokenResponse, AdminUserResponse
from app.security import verify_password, create_access_token, get_current_admin

router = APIRouter(prefix="/api/auth", tags=["Admin Authentication"])

@router.post("/login", response_model=TokenResponse, summary="Admin Login")
async def admin_login(payload: LoginRequest, response: Response):
    """Authenticate administrator or staff member using email and password."""
    clean_email = payload.email.strip().lower()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, email, password_hash, role, is_active, last_login, created_at
            FROM admin_users
            WHERE email = ?
        """, (clean_email,))
        user = cursor.fetchone()

        if not user or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your administrator account has been disabled. Please contact a Super Admin.",
            )

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE admin_users SET last_login = ? WHERE id = ?", (now_str, user["id"]))

        access_token = create_access_token(data={
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user["role"],
            "name": user["name"],
        })

        response.set_cookie(
            key="dogcu_access_token",
            value=access_token,
            httponly=False,
            max_age=86400,
            samesite="lax",
            path="/",
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=AdminUserResponse(
                id=user["id"],
                name=user["name"],
                email=user["email"],
                role=user["role"],
                is_active=bool(user["is_active"]),
                last_login=now_str,
                created_at=user["created_at"],
            ),
        )

@router.get("/me", response_model=AdminUserResponse, summary="Get Current Logged-in Admin")
async def get_current_user_profile(current_user: dict = Depends(get_current_admin)):
    """Retrieve the profile and permissions of the currently authenticated administrator."""
    return AdminUserResponse(
        id=current_user["id"],
        name=current_user["name"],
        email=current_user["email"],
        role=current_user["role"],
        is_active=bool(current_user["is_active"]),
        last_login=current_user["last_login"],
        created_at=current_user.get("created_at", ""),
    )

@router.post("/logout", summary="Admin Logout")
@router.get("/logout", summary="Admin Logout")
async def admin_logout(response: Response):
    """Logout endpoint clearing the session cookie."""
    response.delete_cookie(key="dogcu_access_token", path="/")
    response.delete_cookie(key="access_token", path="/")
    return {"status": "SUCCESS", "message": "Successfully logged out."}
