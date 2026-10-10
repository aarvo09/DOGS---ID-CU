import re
import secrets
import string
import sqlite3
from typing import Optional

TAG_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ" # Readable alphanumeric characters without 0/O, 1/I

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token for QR tag verification."""
    return secrets.token_urlsafe(length)

def generate_tag_uid(conn: sqlite3.Connection) -> str:
    """Generate a unique tag identifier in the format CU-TAG-XXXXXX."""
    cursor = conn.cursor()
    for _ in range(100):
        suffix = "".join(secrets.choice(TAG_ALPHABET) for _ in range(6))
        candidate = f"CU-TAG-{suffix}"
        cursor.execute("SELECT 1 FROM qr_tags WHERE tag_uid = ?", (candidate,))
        if not cursor.fetchone():
            return candidate
    raise RuntimeError("Failed to generate a unique tag_uid after 100 attempts")

def generate_dog_uid(conn: sqlite3.Connection, requested_uid: Optional[str] = None) -> str:
    """
    Validate or generate a unique dog identifier (e.g. CU-DOG-024).
    If requested_uid is provided, validate format and uniqueness.
    Otherwise, automatically generate the next sequential CU-DOG-XXX.
    """
    cursor = conn.cursor()

    if requested_uid:
        clean_uid = requested_uid.strip().upper()
        if not re.match(r"^CU-DOG-[A-Z0-9]+$", clean_uid):
            raise ValueError("Dog UID must follow the format 'CU-DOG-XXX' (alphanumeric characters)")
        cursor.execute("SELECT 1 FROM dogs WHERE dog_uid = ?", (clean_uid,))
        if cursor.fetchone():
            raise ValueError(f"Dog UID '{clean_uid}' already exists in the system")
        return clean_uid

    # Find highest numeric sequence among CU-DOG-NNN
    cursor.execute("SELECT dog_uid FROM dogs WHERE dog_uid LIKE 'CU-DOG-%'")
    rows = cursor.fetchall()
    max_num = 0
    for row in rows:
        match = re.match(r"^CU-DOG-(\d+)$", row["dog_uid"])
        if match:
            max_num = max(max_num, int(match.group(1)))

    next_num = max_num + 1
    return f"CU-DOG-{next_num:03d}"
