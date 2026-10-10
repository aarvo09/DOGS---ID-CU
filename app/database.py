import sqlite3
from contextlib import contextmanager
from typing import Generator
from app.config import DATABASE_PATH

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    return conn

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Admin Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('SUPER_ADMIN', 'ADMIN', 'STAFF')),
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        """)

        # 2. Dogs Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dog_uid TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            gender TEXT NOT NULL,
            approx_age TEXT NOT NULL,
            description TEXT,
            photo_url TEXT,
            status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'MISSING', 'INACTIVE', 'DECEASED', 'TRANSFERRED', 'UNDER_CARE')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. QR Tags Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS qr_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_uid TEXT UNIQUE NOT NULL,
            qr_token TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'INACTIVE', 'LOST', 'DAMAGED', 'UNASSIGNED', 'RETIRED')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 4. Dog Tag Assignments Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dog_tag_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dog_id INTEGER NOT NULL REFERENCES dogs(id) ON DELETE CASCADE,
            tag_id INTEGER NOT NULL REFERENCES qr_tags(id) ON DELETE CASCADE,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            unassigned_at TIMESTAMP,
            assigned_by INTEGER REFERENCES admin_users(id),
            status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'UNASSIGNED', 'SUPERSEDED')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 5. Campus Locations Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS campus_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            latitude REAL,
            longitude REAL,
            area_type TEXT DEFAULT 'ACADEMIC',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 6. Sightings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sightings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dog_id INTEGER NOT NULL REFERENCES dogs(id) ON DELETE CASCADE,
            location_id INTEGER REFERENCES campus_locations(id) ON DELETE SET NULL,
            location_name TEXT,
            latitude REAL,
            longitude REAL,
            accuracy REAL,
            activity TEXT,
            photo_url TEXT,
            note TEXT,
            submitted_by TEXT DEFAULT 'Anonymous Campus Member',
            source TEXT NOT NULL DEFAULT 'PUBLIC' CHECK(source IN ('PUBLIC', 'ADMIN', 'STAFF')),
            is_verified INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'FLAGGED', 'REMOVED')),
            ip_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 7. Reports Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dog_id INTEGER NOT NULL REFERENCES dogs(id) ON DELETE CASCADE,
            report_type TEXT NOT NULL CHECK(report_type IN ('INJURED', 'SICK', 'MISSING', 'WRONG_INFORMATION', 'OTHER')),
            severity TEXT DEFAULT 'MEDIUM' CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
            description TEXT NOT NULL,
            location_id INTEGER REFERENCES campus_locations(id) ON DELETE SET NULL,
            location_name TEXT,
            latitude REAL,
            longitude REAL,
            photo_url TEXT,
            submitted_by TEXT DEFAULT 'Anonymous Campus Member',
            contact_info TEXT,
            status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'UNDER_REVIEW', 'RESOLVED', 'DISMISSED')),
            admin_notes TEXT,
            resolved_by INTEGER REFERENCES admin_users(id),
            resolved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 8. Dog Health Records Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dog_health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dog_id INTEGER NOT NULL REFERENCES dogs(id) ON DELETE CASCADE,
            vaccination_status TEXT NOT NULL DEFAULT 'UNKNOWN',
            last_vaccination_date DATE,
            sterilization_status TEXT NOT NULL DEFAULT 'UNKNOWN',
            health_status TEXT NOT NULL DEFAULT 'HEALTHY',
            notes TEXT,
            updated_by INTEGER REFERENCES admin_users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Indices for optimal query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dogs_uid ON dogs(dog_uid);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_qr_tags_uid ON qr_tags(tag_uid);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dog_tag_active ON dog_tag_assignments(tag_id, status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dog_tag_dog ON dog_tag_assignments(dog_id, status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sightings_dog ON sightings(dog_id, created_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_dog ON reports(dog_id, status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_locations_active ON campus_locations(is_active);")
