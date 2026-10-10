from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Depends
from app.database import get_db
from app.models import AdminUserCreate, AdminUserUpdate, AdminUserResponse
from app.security import require_roles, hash_password

router = APIRouter(prefix="/api/admin/users", tags=["Admin - Users"])

@router.get("", response_model=List[AdminUserResponse], summary="List Admin Users")
async def list_admin_users(current_user: dict = Depends(require_roles(["SUPER_ADMIN"]))):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, role, is_active, last_login, created_at FROM admin_users ORDER BY id ASC")
        return [
            AdminUserResponse(
                id=r["id"],
                name=r["name"],
                email=r["email"],
                role=r["role"],
                is_active=bool(r["is_active"]),
                last_login=r["last_login"],
                created_at=r["created_at"],
            ) for r in cursor.fetchall()
        ]

@router.post("", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED, summary="Create Admin User")
async def create_admin_user(
    payload: AdminUserCreate,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN"])),
):
    clean_email = payload.email.strip().lower()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM admin_users WHERE email = ?", (clean_email,))
        if cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered.")

        pw_hash = hash_password(payload.password)
        cursor.execute("""
            INSERT INTO admin_users (name, email, password_hash, role, is_active)
            VALUES (?, ?, ?, ?, 1)
        """, (payload.name.strip(), clean_email, pw_hash, payload.role))
        user_id = cursor.lastrowid

        cursor.execute("SELECT id, name, email, role, is_active, last_login, created_at FROM admin_users WHERE id = ?", (user_id,))
        r = cursor.fetchone()
        return AdminUserResponse(
            id=r["id"],
            name=r["name"],
            email=r["email"],
            role=r["role"],
            is_active=bool(r["is_active"]),
            last_login=r["last_login"],
            created_at=r["created_at"],
        )

@router.patch("/{user_id}", response_model=AdminUserResponse, summary="Update Admin User")
async def update_admin_user(
    user_id: int,
    payload: AdminUserUpdate,
    current_user: dict = Depends(require_roles(["SUPER_ADMIN"])),
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM admin_users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        fields = []
        values = []
        if payload.name is not None:
            fields.append("name = ?")
            values.append(payload.name.strip())
        if payload.role is not None:
            fields.append("role = ?")
            values.append(payload.role)
        if payload.is_active is not None:
            fields.append("is_active = ?")
            values.append(1 if payload.is_active else 0)
        if payload.password is not None:
            fields.append("password_hash = ?")
            values.append(hash_password(payload.password))

        if fields:
            fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(user_id)
            cursor.execute(f"UPDATE admin_users SET {', '.join(fields)} WHERE id = ?", values)

        cursor.execute("SELECT id, name, email, role, is_active, last_login, created_at FROM admin_users WHERE id = ?", (user_id,))
        r = cursor.fetchone()
        return AdminUserResponse(
            id=r["id"],
            name=r["name"],
            email=r["email"],
            role=r["role"],
            is_active=bool(r["is_active"]),
            last_login=r["last_login"],
            created_at=r["created_at"],
        )
