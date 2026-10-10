import sqlite3
from datetime import datetime, timezone, timedelta
from app.database import get_db, init_db
from app.security import hash_password
from app.id_generator import generate_secure_token

def seed_database():
    """Populate database with official demo dataset for Chandigarh University."""
    init_db()

    with get_db() as conn:
        cursor = conn.cursor()

        # Check if already seeded
        cursor.execute("SELECT COUNT(*) as cnt FROM admin_users")
        if cursor.fetchone()["cnt"] > 0:
            print("Database already contains data. Skipping re-seed.")
            return

        print("Seeding initial database records...")

        # 1. Admin Users
        superadmin_pw = hash_password("Admin@12345")
        staff_pw = hash_password("Staff@12345")

        cursor.execute("""
            INSERT INTO admin_users (name, email, password_hash, role, is_active)
            VALUES (?, ?, ?, ?, 1)
        """, ("CU Animal Welfare Lead", "admin@cumail.in", superadmin_pw, "SUPER_ADMIN"))
        admin_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO admin_users (name, email, password_hash, role, is_active)
            VALUES (?, ?, ?, ?, 1)
        """, ("Campus Rescue Staff", "staff@cumail.in", staff_pw, "STAFF"))
        staff_id = cursor.lastrowid

        # 2. Campus Locations (Chandigarh University) - 7 Canonical Locations
        locations = [
            ("Academic Block E", "Computer Science, AI & Engineering Labs", 30.7695, 76.5760, "ACADEMIC"),
            ("Academic Block F", "University Business School & Seminar Halls", 30.7700, 76.5770, "ACADEMIC"),
            ("Hostel A", "North Hostel Blocks promenade", 30.7710, 76.5740, "HOSTEL"),
            ("Hostel B", "South Hostel Blocks & recreation park", 30.7660, 76.5760, "HOSTEL"),
            ("Field", "Cricket ground, sports complex and gym", 30.7670, 76.5730, "SPORTS"),
            ("Pond", "Central campus lawn and fountain pond", 30.7685, 76.5755, "OUTDOOR"),
            ("Parking", "Main campus vehicle parking", 30.7650, 76.5780, "PARKING"),
        ]

        loc_ids = {}
        for name, desc, lat, lon, area in locations:
            cursor.execute("""
                INSERT INTO campus_locations (name, description, latitude, longitude, area_type, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (name, desc, lat, lon, area))
            loc_ids[name] = cursor.lastrowid

        # 3. Dogs (Bruno CU-DOG-024, Milo CU-DOG-025, Luna CU-DOG-026)
        dogs_data = [
            (
                "CU-DOG-024",
                "Bruno",
                "Male",
                "3 years",
                "Friendly golden-brown indie dog. Beloved by students near Block 2 and the food court. Extremely gentle and approachable.",
                "https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=600&q=80",
                "ACTIVE",
            ),
            (
                "CU-DOG-025",
                "Milo",
                "Male",
                "2 years",
                "High-energy black and white indie dog. Frequently seen around sports grounds and student hostel pathways.",
                "https://images.unsplash.com/photo-1587300003388-59208cc962cb?auto=format&fit=crop&w=600&q=80",
                "ACTIVE",
            ),
            (
                "CU-DOG-026",
                "Luna",
                "Female",
                "4 years",
                "Calm and affectionate tan indie dog with white paws. Usually rests near the Library Hub and Academic Block 1.",
                "https://images.unsplash.com/photo-1537151625747-768eb6cf92b2?auto=format&fit=crop&w=600&q=80",
                "ACTIVE",
            ),
        ]

        dog_ids = {}
        for uid, name, gender, age, desc, photo, st in dogs_data:
            cursor.execute("""
                INSERT INTO dogs (dog_uid, name, gender, approx_age, description, photo_url, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (uid, name, gender, age, desc, photo, st))
            dog_ids[uid] = cursor.lastrowid

        # 4. QR Tags & Assignments
        tags_data = [
            ("CU-TAG-8F42K9", "CU-DOG-024"), # Bruno
            ("CU-TAG-9M31P2", "CU-DOG-025"), # Milo
            ("CU-TAG-4K77X1", "CU-DOG-026"), # Luna
            ("CU-TAG-SPAREE", None),          # Unassigned spare tag for testing
            ("CU-TAG-RBX101", None),          # Static Tag 05 (RoboX Club)
            ("CU-TAG-RBX102", None),          # Static Tag 06 (RoboX Club)
            ("CU-TAG-RBX103", None),          # Static Tag 07 (RoboX Club)
            ("CU-TAG-RBX104", None),          # Static Tag 08 (RoboX Club)
            ("CU-TAG-RBX105", None),          # Static Tag 09 (RoboX Club)
            ("CU-TAG-RBX106", None),          # Static Tag 10 (RoboX Club)
        ]

        tag_ids = {}
        for tag_uid, assigned_dog_uid in tags_data:
            cursor.execute("""
                INSERT INTO qr_tags (tag_uid, qr_token, status)
                VALUES (?, ?, 'ACTIVE')
            """, (tag_uid, generate_secure_token()))
            t_id = cursor.lastrowid
            tag_ids[tag_uid] = t_id

            if assigned_dog_uid:
                d_id = dog_ids[assigned_dog_uid]
                cursor.execute("""
                    INSERT INTO dog_tag_assignments (dog_id, tag_id, assigned_by, status)
                    VALUES (?, ?, ?, 'ACTIVE')
                """, (d_id, t_id, admin_id))

        # 5. Health Records
        health_data = [
            (dog_ids["CU-DOG-024"], "UP_TO_DATE", "2026-03-15", "STERILIZED", "HEALTHY", "Vaccinated for Rabies + DHPPiL. Microchipped collar band applied."),
            (dog_ids["CU-DOG-025"], "UP_TO_DATE", "2026-04-10", "STERILIZED", "HEALTHY", "Vaccinated for Rabies. Excellent general health."),
            (dog_ids["CU-DOG-026"], "UP_TO_DATE", "2026-02-20", "STERILIZED", "NEEDS_ATTENTION", "Mild seasonal skin allergy under observation. Healing well."),
        ]
        for d_id, vacc, vdate, ster, hst, notes in health_data:
            cursor.execute("""
                INSERT INTO dog_health_records (dog_id, vaccination_status, last_vaccination_date, sterilization_status, health_status, notes, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (d_id, vacc, vdate, ster, hst, notes, admin_id))

        # 6. Sighting History (Chronological demonstration)
        now = datetime.now(timezone.utc)
        sightings_data = [
            # Bruno sightings (demonstrates last-seen location progression)
            (
                dog_ids["CU-DOG-024"],
                loc_ids["Hostel A"],
                "Hostel A",
                "Sleeping",
                "Resting in the hostel courtyard morning shade",
                (now - timedelta(hours=3, minutes=10)).strftime("%Y-%m-%d %H:%M:%S"),
            ),
            (
                dog_ids["CU-DOG-024"],
                loc_ids["Pond"],
                "Pond",
                "With Students",
                "Playing near pond benches, very energetic",
                (now - timedelta(hours=1, minutes=20)).strftime("%Y-%m-%d %H:%M:%S"),
            ),
            (
                dog_ids["CU-DOG-024"],
                loc_ids["Academic Block E"],
                "Academic Block E",
                "Resting",
                "Sitting outside the Block E foyer",
                (now - timedelta(minutes=14)).strftime("%Y-%m-%d %H:%M:%S"),
            ),
            # Milo sightings
            (
                dog_ids["CU-DOG-025"],
                loc_ids["Field"],
                "Field",
                "Playing",
                "Running across athletic field perimeter",
                (now - timedelta(hours=1, minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
            ),
            (
                dog_ids["CU-DOG-025"],
                loc_ids["Parking"],
                "Parking",
                "Roaming",
                "Walking peacefully along parking entrance",
                (now - timedelta(minutes=35)).strftime("%Y-%m-%d %H:%M:%S"),
            ),
            # Luna sightings
            (
                dog_ids["CU-DOG-026"],
                loc_ids["Hostel B"],
                "Hostel B",
                "Resting",
                "Relaxing under the courtyard shade",
                (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            ),
            (
                dog_ids["CU-DOG-026"],
                loc_ids["Academic Block F"],
                "Academic Block F",
                "Sleeping",
                "Resting peacefully near Academic Block F ramp",
                (now - timedelta(minutes=48)).strftime("%Y-%m-%d %H:%M:%S"),
            ),
        ]

        for d_id, l_id, l_name, act, note, created_dt in sightings_data:
            cursor.execute("""
                INSERT INTO sightings (
                    dog_id, location_id, location_name, activity, note, submitted_by, source, is_verified, status, created_at
                ) VALUES (?, ?, ?, ?, ?, 'Campus Student', 'PUBLIC', 1, 'ACTIVE', ?)
            """, (d_id, l_id, l_name, act, note, created_dt))

        # 7. Demo Reports
        cursor.execute("""
            INSERT INTO reports (
                dog_id, report_type, severity, description, location_id, location_name, submitted_by, status, admin_notes, resolved_by, resolved_at
            ) VALUES (?, 'OTHER', 'LOW', 'Minor ear scratch observed yesterday during morning walk', ?, 'Central Library Hub', 'Library Volunteer', 'RESOLVED', 'Examined by campus vet; antiseptic spray applied. Healing cleanly.', ?, ?)
        """, (dog_ids["CU-DOG-026"], loc_ids["Central Library Hub"], admin_id, (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")))

        print("Seeding completed successfully!")
        print(f"Created Admin: admin@cumail.in / Admin@12345")
        print(f"Created Staff: staff@cumail.in / Staff@12345")
        print(f"Created Dogs: Bruno (CU-DOG-024), Milo (CU-DOG-025), Luna (CU-DOG-026)")
        print(f"Created QR Tags: CU-TAG-8F42K9, CU-TAG-9M31P2, CU-TAG-4K77X1, CU-TAG-SPAREE")

if __name__ == "__main__":
    seed_database()
