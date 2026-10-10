import os
import unittest
import tempfile
from pathlib import Path
from starlette.testclient import TestClient

# Set temporary test database environment variable before importing app modules
test_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_PATH"] = test_db_file.name

from app.database import init_db, get_db
from app.main import app
from app.security import hash_password

class DogCUSystemTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize fresh DB schema for tests
        init_db()
        cls.client = TestClient(app)

        # Seed test admin user
        with get_db() as conn:
            cursor = conn.cursor()
            pw_hash = hash_password("AdminSecret123")
            cursor.execute("SELECT id FROM admin_users WHERE email = 'admin.test@cumail.in'")
            row = cursor.fetchone()
            if row:
                cls.admin_id = row["id"]
                cursor.execute("UPDATE admin_users SET password_hash = ? WHERE id = ?", (pw_hash, cls.admin_id))
            else:
                cursor.execute("""
                    INSERT INTO admin_users (name, email, password_hash, role, is_active)
                    VALUES ('CU Admin', 'admin.test@cumail.in', ?, 'SUPER_ADMIN', 1)
                """, (pw_hash,))
                cls.admin_id = cursor.lastrowid

            # Seed a staff user
            staff_pw = hash_password("StaffSecret123")
            cursor.execute("SELECT id FROM admin_users WHERE email = 'staff.test@cumail.in'")
            srow = cursor.fetchone()
            if srow:
                cls.staff_id = srow["id"]
                cursor.execute("UPDATE admin_users SET password_hash = ? WHERE id = ?", (staff_pw, cls.staff_id))
            else:
                cursor.execute("""
                    INSERT INTO admin_users (name, email, password_hash, role, is_active)
                    VALUES ('CU Staff', 'staff.test@cumail.in', ?, 'STAFF', 1)
                """, (staff_pw,))
                cls.staff_id = cursor.lastrowid

            # Seed campus locations
            cursor.execute("SELECT id FROM campus_locations WHERE name = 'Academic Block 2'")
            l1 = cursor.fetchone()
            if l1:
                cls.loc_block2_id = l1["id"]
            else:
                cursor.execute("""
                    INSERT INTO campus_locations (name, description, area_type, is_active)
                    VALUES ('Academic Block 2', 'Computing and Engineering Quad', 'ACADEMIC', 1)
                """)
                cls.loc_block2_id = cursor.lastrowid

            cursor.execute("SELECT id FROM campus_locations WHERE name = 'Central Lawn'")
            l2 = cursor.fetchone()
            if l2:
                cls.loc_lawn_id = l2["id"]
            else:
                cursor.execute("""
                    INSERT INTO campus_locations (name, description, area_type, is_active)
                    VALUES ('Central Lawn', 'Main grass lawn and fountain', 'OUTDOOR', 1)
                """)
                cls.loc_lawn_id = cursor.lastrowid

        # Authenticate and obtain JWT
        login_res = cls.client.post("/api/auth/login", json={
            "email": "admin.test@cumail.in",
            "password": "AdminSecret123",
        })
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        cls.token = login_res.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(test_db_file.name)
        except Exception:
            pass

    def test_01_create_bruno(self):
        """Test 1: Create Bruno (CU-DOG-024)"""
        payload = {
            "dog_uid": "CU-DOG-024",
            "name": "Bruno",
            "gender": "Male",
            "approx_age": "3 years",
            "description": "Friendly campus dog near Academic Block 2",
            "photo_url": "https://example.com/bruno.jpg",
            "status": "ACTIVE"
        }
        res = self.client.post("/api/admin/dogs", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["dog_uid"], "CU-DOG-024")
        self.assertEqual(data["name"], "Bruno")
        self.assertEqual(data["gender"], "Male")
        self.__class__.bruno_db_id = data["id"]

    def test_02_create_qr_tag(self):
        """Test 2: Create QR (CU-TAG-8F42K9)"""
        # Create tag directly or verify tag generation
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO qr_tags (tag_uid, qr_token, status)
                VALUES ('CU-TAG-8F42K9', 'secure_token_8f42k9_test', 'ACTIVE')
            """)
            self.__class__.bruno_tag_id = cursor.lastrowid

        res = self.client.get(f"/api/admin/tags/{self.bruno_tag_id}", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["tag_uid"], "CU-TAG-8F42K9")
        self.assertEqual(res.json()["status"], "ACTIVE")

    def test_03_assign_qr_to_bruno(self):
        """Test 3: Assign QR to Bruno"""
        res = self.client.post(
            f"/api/admin/tags/{self.bruno_tag_id}/assign",
            json={"dog_id": self.bruno_db_id},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["dog_uid"], "CU-DOG-024")
        self.assertEqual(data["tag_uid"], "CU-TAG-8F42K9")

    def test_04_open_tag_resolves_to_bruno(self):
        """Test 4: Open /t/CU-TAG-8F42K9. Verify it resolves to Bruno."""
        # Test JSON resolution
        res_json = self.client.get("/t/CU-TAG-8F42K9?format=json")
        self.assertEqual(res_json.status_code, 200)
        data = res_json.json()
        self.assertEqual(data["status"], "ASSIGNED")
        self.assertEqual(data["dog_uid"], "CU-DOG-024")
        self.assertEqual(data["dog_name"], "Bruno")
        self.assertEqual(data["redirect_url"], "/dog/CU-DOG-024")

        # Test browser scan 302 redirect
        res_redirect = self.client.get("/t/CU-TAG-8F42K9", follow_redirects=False)
        self.assertEqual(res_redirect.status_code, 302)
        self.assertEqual(res_redirect.headers["location"], "/dog/CU-DOG-024")

    def test_05_update_bruno_info_same_qr_resolves(self):
        """
        Test 5: Change Bruno's information.
        Verify the SAME QR still opens Bruno with updated information.
        """
        update_payload = {
            "approx_age": "4 years",
            "description": "Friendly campus dog, now 4 years old, loves treats."
        }
        res_patch = self.client.patch(
            f"/api/admin/dogs/{self.bruno_db_id}",
            json=update_payload,
            headers=self.headers,
        )
        self.assertEqual(res_patch.status_code, 200)
        self.assertEqual(res_patch.json()["approx_age"], "4 years")

        # Verify QR still resolves to Bruno
        res_qr = self.client.get("/t/CU-TAG-8F42K9?format=json")
        self.assertEqual(res_qr.status_code, 200)
        self.assertEqual(res_qr.json()["dog_uid"], "CU-DOG-024")

        # Verify public profile has updated age
        res_profile = self.client.get("/api/dogs/CU-DOG-024")
        self.assertEqual(res_profile.status_code, 200)
        self.assertEqual(res_profile.json()["approx_age"], "4 years")
        self.assertEqual(res_profile.json()["name"], "Bruno")

    def test_06_public_sighting_academic_block_2(self):
        """Test 6: Public user submits Bruno at Academic Block 2. Verify sighting created."""
        sighting_payload = {
            "location_id": self.loc_block2_id,
            "activity": "Sleeping",
            "note": "Resting under the tree shade outside Block 2",
            "submitted_by": "Aman (CSE Student)"
        }
        res = self.client.post("/api/dogs/CU-DOG-024/sightings", json=sighting_payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["dog_uid"], "CU-DOG-024")
        self.assertIn("sighting_id", data)
        self.assertEqual(data["last_seen"]["location"], "Academic Block 2")
        self.__class__.sighting_1_id = data["sighting_id"]

    def test_07_public_sighting_central_lawn_both_in_history(self):
        """
        Test 7: Another public user submits Bruno at Central Lawn.
        Verify both sightings remain in history.
        """
        sighting_payload = {
            "location_id": self.loc_lawn_id,
            "activity": "Playing",
            "note": "Playing with students on Central Lawn",
            "submitted_by": "Rhea (Student)"
        }
        res = self.client.post("/api/dogs/CU-DOG-024/sightings", json=sighting_payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.__class__.sighting_2_id = data["sighting_id"]

        # Check full history contains BOTH sightings
        res_history = self.client.get("/api/dogs/CU-DOG-024/sightings")
        self.assertEqual(res_history.status_code, 200)
        history = res_history.json()
        self.assertGreaterEqual(len(history), 2)
        sighting_ids = [s["id"] for s in history]
        self.assertIn(self.sighting_1_id, sighting_ids)
        self.assertIn(self.sighting_2_id, sighting_ids)

    def test_08_public_profile_shows_newest_sighting_as_last_location(self):
        """Test 8: Verify Bruno's public page now shows the newest valid sighting as the latest location."""
        res = self.client.get("/api/dogs/CU-DOG-024")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsNotNone(data["last_seen"])
        self.assertEqual(data["last_seen"]["location"], "Central Lawn")
        self.assertEqual(data["last_seen"]["activity"], "Playing")

    def test_09_create_milo_different_qr_does_not_open_bruno(self):
        """Test 9: Create Milo (CU-DOG-025), give different QR, verify Milo's QR does NOT open Bruno."""
        milo_payload = {
            "dog_uid": "CU-DOG-025",
            "name": "Milo",
            "gender": "Male",
            "approx_age": "2 years",
            "description": "Energetic black and white campus dog",
            "status": "ACTIVE"
        }
        res_milo = self.client.post("/api/admin/dogs", json=milo_payload, headers=self.headers)
        self.assertEqual(res_milo.status_code, 201)
        milo_id = res_milo.json()["id"]

        # Create tag for Milo
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO qr_tags (tag_uid, qr_token, status)
                VALUES ('CU-TAG-9M31P2', 'secure_token_milo_test', 'ACTIVE')
            """)
            milo_tag_id = cursor.lastrowid

        # Assign tag to Milo
        res_assign = self.client.post(
            f"/api/admin/tags/{milo_tag_id}/assign",
            json={"dog_id": milo_id},
            headers=self.headers,
        )
        self.assertEqual(res_assign.status_code, 200)

        # Resolve Milo's QR: must open Milo, NEVER Bruno
        res_resolve = self.client.get("/t/CU-TAG-9M31P2?format=json")
        self.assertEqual(res_resolve.status_code, 200)
        self.assertEqual(res_resolve.json()["dog_uid"], "CU-DOG-025")
        self.assertEqual(res_resolve.json()["dog_name"], "Milo")
        self.assertNotEqual(res_resolve.json()["dog_uid"], "CU-DOG-024")

    def test_10_deactivate_bruno_qr_not_public(self):
        """Test 10: Deactivate Bruno's QR. Verify the QR no longer exposes Bruno publicly."""
        # Deactivate tag
        res_deact = self.client.patch(
            f"/api/admin/tags/{self.bruno_tag_id}",
            json={"status": "INACTIVE"},
            headers=self.headers,
        )
        self.assertEqual(res_deact.status_code, 200)
        self.assertEqual(res_deact.json()["status"], "INACTIVE")

        # Attempt to scan deactivated QR
        res_scan = self.client.get("/t/CU-TAG-8F42K9?format=json")
        self.assertEqual(res_scan.status_code, 403)
        data = res_scan.json()
        self.assertEqual(data["status"], "INACTIVE")
        self.assertEqual(data["message"], "THIS TAG IS CURRENTLY INACTIVE")
        # Ensure Bruno is not exposed
        self.assertNotIn("dog_uid", data)

        # Re-activate for subsequent tests
        self.client.patch(
            f"/api/admin/tags/{self.bruno_tag_id}",
            json={"status": "ACTIVE"},
            headers=self.headers,
        )

    def test_11_unassign_bruno_tag(self):
        """Test 11: Unassign Bruno's tag. Verify the tag becomes unassigned."""
        res_unassign = self.client.post(
            f"/api/admin/tags/{self.bruno_tag_id}/unassign",
            headers=self.headers,
        )
        self.assertEqual(res_unassign.status_code, 200)

        # Attempt to scan unassigned QR
        res_scan = self.client.get("/t/CU-TAG-8F42K9?format=json")
        self.assertEqual(res_scan.status_code, 404)
        data = res_scan.json()
        self.assertEqual(data["status"], "UNASSIGNED")
        self.assertEqual(data["message"], "THIS TAG IS NOT CURRENTLY ASSIGNED")

    def test_12_reassign_same_tag_to_another_dog_preserves_history(self):
        """
        Test 12: Assign the same tag to another dog.
        Verify the QR now resolves to the newly assigned dog while preserving old assignment history.
        """
        # Create Luna
        luna_payload = {
            "dog_uid": "CU-DOG-026",
            "name": "Luna",
            "gender": "Female",
            "approx_age": "4 years",
            "status": "ACTIVE"
        }
        res_luna = self.client.post("/api/admin/dogs", json=luna_payload, headers=self.headers)
        self.assertEqual(res_luna.status_code, 201)
        luna_id = res_luna.json()["id"]

        # Assign Bruno's previous tag (CU-TAG-8F42K9) to Luna
        res_assign = self.client.post(
            f"/api/admin/tags/{self.bruno_tag_id}/assign",
            json={"dog_id": luna_id},
            headers=self.headers,
        )
        self.assertEqual(res_assign.status_code, 200)

        # Verify QR now resolves to LUNA
        res_qr = self.client.get("/t/CU-TAG-8F42K9?format=json")
        self.assertEqual(res_qr.status_code, 200)
        self.assertEqual(res_qr.json()["dog_uid"], "CU-DOG-026")
        self.assertEqual(res_qr.json()["dog_name"], "Luna")

        # Verify assignment history contains BOTH assignments (Bruno's historical + Luna's active)
        res_history = self.client.get(f"/api/admin/tags/{self.bruno_tag_id}/history", headers=self.headers)
        self.assertEqual(res_history.status_code, 200)
        history = res_history.json()
        self.assertGreaterEqual(len(history), 2)
        dog_uids_in_history = [h["dog_uid"] for h in history]
        self.assertIn("CU-DOG-024", dog_uids_in_history) # Bruno
        self.assertIn("CU-DOG-026", dog_uids_in_history) # Luna

    def test_13_nonexistent_qr_returns_not_registered(self):
        """Verify invalid/unregistered QR returns 'QR TAG NOT REGISTERED' without leaking DB errors."""
        res = self.client.get("/t/CU-TAG-DOESNOTEXIST?format=json")
        self.assertEqual(res.status_code, 404)
        data = res.json()
        self.assertEqual(data["status"], "NOT_FOUND")
        self.assertEqual(data["message"], "QR TAG NOT REGISTERED")

    def test_14_emergency_report_submission(self):
        """Verify emergency injury report creates a pending admin ticket."""
        report_payload = {
            "report_type": "INJURED",
            "severity": "HIGH",
            "description": "Limping on right front paw near library entrance",
            "location_name": "Library Steps",
            "submitted_by": "Kunal (Faculty)",
            "contact_info": "+91-9876543210"
        }
        res = self.client.post("/api/dogs/CU-DOG-024/reports", json=report_payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        report_id = data["report_id"]

        # Verify admin can view and resolve report
        res_admin = self.client.get(f"/api/admin/reports/{report_id}", headers=self.headers)
        self.assertEqual(res_admin.status_code, 200)
        self.assertEqual(res_admin.json()["severity"], "HIGH")

        # Resolve report
        res_resolve = self.client.patch(
            f"/api/admin/reports/{report_id}",
            json={"status": "RESOLVED", "admin_notes": "Vet examined paw; thorn removed, bandage applied."},
            headers=self.headers,
        )
        self.assertEqual(res_resolve.status_code, 200)
        self.assertEqual(res_resolve.json()["status"], "RESOLVED")

    def test_15_dashboard_metrics(self):
        """Verify dashboard endpoint returns operational summary data."""
        res = self.client.get("/api/admin/dashboard", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("summary", data)
        self.assertGreaterEqual(data["summary"]["total_dogs"], 3)
        self.assertIn("recent_sightings", data)
        self.assertIn("dogs_needing_attention", data)

    def test_16_handmade_design_tokens_and_utilities(self):
        """Verify static/css/handmade.css defines all required design tokens and 10 handmade effect utilities."""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        handmade_css_path = os.path.join(base_dir, "static", "css", "handmade.css")
        self.assertTrue(os.path.exists(handmade_css_path), "handmade.css must exist")
        
        with open(handmade_css_path, "r", encoding="utf-8") as f:
            css = f.read()

        # Required Colors
        for token in ["--cu-red", "--ink", "--paper", "--paper-dark", "--muted-green", "--soft-gray"]:
            self.assertIn(token, css, f"Missing color token: {token}")

        # Required Typography Tokens
        self.assertIn("--font-body", css)
        self.assertIn("--font-display", css)
        self.assertIn("--font-handwritten", css)

        # Spacing System
        for space in ["--space-xs", "--space-sm", "--space-md", "--space-lg", "--space-xl", "--space-2xl"]:
            self.assertIn(space, css, f"Missing spacing token: {space}")

        # The 10 Reusable Handmade Effect Utilities
        effects = [
            ".rough-border",            # rough borders
            ".marker-underline",        # marker underline
            ".paper-texture",           # paper texture
            ".torn-edge-bottom",        # torn-paper edge
            ".rotate-slight-left",      # slight rotation
            ".tape-strip",              # tape effect
            ".handwritten-annotation",  # handwritten annotation
            ".sketch-shadow",           # sketch shadow
            ".imperfect-circle",        # imperfect circle
            ".marker-highlight",        # marker highlight
        ]
        for effect in effects:
            self.assertIn(effect, css, f"Missing handmade effect utility: {effect}")

    def test_17_components_showcase_serves_tokens_and_utilities(self):
        """Verify /components serves the design tokens palette and the 10 handmade effect utilities."""
        res = self.client.get("/components")
        self.assertEqual(res.status_code, 200)
        html = res.text

        # Tokens in HTML
        for token in ["--cu-red", "--ink", "--paper", "--paper-dark", "--muted-green", "--soft-gray"]:
            self.assertIn(token, html)

        # Handmade effect utilities in HTML
        for cls in ["rough-border", "marker-underline", "torn-edge-bottom", "tape-strip", "imperfect-circle", "marker-highlight"]:
            self.assertIn(cls, html)

    def test_18_individual_dog_profile_page_structure(self):
        """Verify the individual dog profile page (/dog/CU-DOG-024) matches the physical field notebook spec."""
        res = self.client.get("/dog/CU-DOG-024")
        self.assertEqual(res.status_code, 200)
        html = res.text

        # 1. Top Identity & Back Arrow
        self.assertIn("CU Campus Dogs", html)
        self.assertIn("Campus Dogs", html)
        self.assertIn("handmade-back-link", html)

        # 2. Critical rule: MUST NOT contain pack switcher chips or other dogs
        self.assertNotIn("demo-selector-group", html)
        self.assertNotIn("Pack Dossiers", html)

        # 3. Main Photograph with tape and handwritten annotation
        self.assertIn("Hey! I'm Bruno", html)
        self.assertIn("polaroid-card", html)
        self.assertIn("tape-strip", html)

        # 4. Dog Identity & Registered Sticker
        self.assertIn("BRUNO", html)
        self.assertIn("CU-DOG-024", html)
        self.assertIn("REGISTERED CAMPUS DOG", html)
        self.assertIn("handmade-info-cluster", html)

        # 5. Dog Tag with QR code
        self.assertIn("physical-dog-tag-card", html)
        self.assertIn("data:image/png;base64,", html) # QR code embedded

        # 6. Personality Paper Note
        self.assertIn("Personality &amp; Habits", html)
        self.assertIn("Professional napper", html)

        # 7. Primary Action Button (I SAW THIS DOG ->)
        self.assertIn("I SAW THIS DOG ➔", html)
        self.assertIn("/dog/CU-DOG-024/sighting", html)

        # 8. Secondary Actions (View Last Location, Report an Issue)
        self.assertIn("VIEW LAST LOCATION ➔", html)
        self.assertIn("/dog/CU-DOG-024/location", html)
        self.assertIn("REPORT AN ISSUE ➔", html)
        self.assertIn("/dog/CU-DOG-024/report", html)

        # 9. Health & Care Section
        self.assertIn("Health &amp; Care Records", html)
        self.assertIn("Vaccination", html)
        self.assertIn("Sterilization", html)

        # 10. Last Spotted Campus Map Section
        self.assertIn("LAST SPOTTED", html)
        self.assertIn("campus-map-box", html)
        self.assertIn("Bruno was seen here last!", html)
        self.assertIn("map-zoom-in-btn", html)
        self.assertIn("map-zoom-out-btn", html)
        self.assertIn("map-zoom-fit-btn", html)

        # 11. Recent Sightings Log
        self.assertIn("Recent Sightings Log", html)

        # 12. Bottom Illustrated Doodle
        self.assertIn("sleeping_dog_doodle.png", html)

    def test_19_dog_not_found_behavior(self):
        """Verify non-existent dog ID returns HTTP 404 with friendly hand-drawn error page."""
        res = self.client.get("/dog/CU-DOG-NONEXISTENT")
        self.assertEqual(res.status_code, 404)
        html = res.text
        self.assertIn("Dog Not Found", html)
        self.assertIn("CU-DOG-NONEXISTENT", html)
    def test_20_time_aware_campus_map(self):
        """Verify time-aware campus map resolution (Day: 8 AM - 8 PM, Night: 8 PM - 8 AM)."""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        day_map = os.path.join(base_dir, "static", "assets", "maps", "campus-map-day.png")
        night_map = os.path.join(base_dir, "static", "assets", "maps", "campus-map-night.png")
        self.assertTrue(os.path.exists(day_map), "Day map must exist in static/assets/maps/campus-map-day.png")
        self.assertTrue(os.path.exists(night_map), "Night map must exist in static/assets/maps/campus-map-night.png")

        # Test both map assets return HTTP 200
        res_day = self.client.get("/static/assets/maps/campus-map-day.png")
        self.assertEqual(res_day.status_code, 200)

        res_night = self.client.get("/static/assets/maps/campus-map-night.png")
        self.assertEqual(res_night.status_code, 200)

        # Profile includes time badge, switch button, and map data attributes
        res_profile = self.client.get("/dog/CU-DOG-024")
        self.assertEqual(res_profile.status_code, 200)
        self.assertIn("map-time-badge", res_profile.text)
        self.assertIn("map-toggle-btn", res_profile.text)
        self.assertIn("data-day-src", res_profile.text)
        self.assertIn("data-night-src", res_profile.text)
        self.assertIn("sighting-map-reference", res_profile.text)

    def test_21_public_scan_resolves_directly_to_single_dog_profile(self):
        """Verify QR scan resolves directly to specific dog profile, never a generic directory (Section 1)."""
        fresh_client = TestClient(app, follow_redirects=False)
        res = fresh_client.get("/t/CU-TAG-8F42K9")
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.headers["location"].startswith("/dog/"))
        self.assertNotIn("all", res.headers["location"].lower())

    def test_22_public_dog_profile_shows_staff_login_link(self):
        """Verify public user sees dog profile with discreet Staff Login link."""
        fresh_client = TestClient(app, follow_redirects=False)
        res = fresh_client.get("/dog/CU-DOG-024")
        self.assertEqual(res.status_code, 200)
        self.assertIn("BRUNO", res.text)
        self.assertIn("Staff Login", res.text)
        self.assertNotIn("admin-floating-status-bar", res.text)

    def test_23_admin_dashboard_requires_login(self):
        """Unauthenticated access to /admin redirects to /admin/login."""
        fresh_client = TestClient(app, follow_redirects=False)
        res = fresh_client.get("/admin")
        self.assertEqual(res.status_code, 303)
        self.assertIn("/admin/login", res.headers["location"])

    def test_24_admin_login_success_and_cookie(self):
        """Admin login succeeds with credentials and sets persistent auth cookie."""
        fresh_client = TestClient(app, follow_redirects=False)
        res = fresh_client.post("/admin/login", data={
            "email": "admin.test@cumail.in",
            "password": "AdminSecret123",
            "next": "/admin"
        })
        self.assertEqual(res.status_code, 303)
        self.assertEqual(res.headers["location"], "/admin")
        self.assertIn("dogcu_access_token", res.headers.get("set-cookie", ""))

    def test_25_admin_dashboard_accessible_with_cookie(self):
        """Authenticated admin can load the full DOGCU management dashboard."""
        fresh_client = TestClient(app, follow_redirects=False)
        login_res = fresh_client.post("/admin/login", data={
            "email": "admin.test@cumail.in",
            "password": "AdminSecret123",
            "next": "/admin"
        })
        token = login_res.cookies.get("dogcu_access_token")

        client_auth = TestClient(app, cookies={"dogcu_access_token": token})
        res = client_auth.get("/admin")
        self.assertEqual(res.status_code, 200)
        self.assertIn("DOGCU Admin Portal", res.text)
        self.assertIn("CU-DOG-024", res.text)

    def test_26_admin_viewing_dog_profile_has_quick_edit_mode(self):
        """When admin scans/opens a dog profile while logged in, in-page edit controls appear."""
        fresh_client = TestClient(app, follow_redirects=False)
        login_res = fresh_client.post("/admin/login", data={
            "email": "admin.test@cumail.in",
            "password": "AdminSecret123",
            "next": "/admin"
        })
        token = login_res.cookies.get("dogcu_access_token")

        client_auth = TestClient(app, cookies={"dogcu_access_token": token})
        res = client_auth.get("/dog/CU-DOG-024")
        self.assertEqual(res.status_code, 200)
        self.assertIn("admin-floating-status-bar", res.text)
        self.assertIn("Admin Mode", res.text)
        self.assertIn("Edit Bruno", res.text)
        self.assertIn("edit-dog-modal", res.text)

    def test_27_admin_update_dog_info_from_form(self):
        """Admin can submit updates to dog profile and be redirected back to the profile with live updates."""
        fresh_client = TestClient(app, follow_redirects=False)
        login_res = fresh_client.post("/admin/login", data={
            "email": "admin.test@cumail.in",
            "password": "AdminSecret123",
            "next": "/admin"
        })
        token = login_res.cookies.get("dogcu_access_token")

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM dogs WHERE dog_uid = 'CU-DOG-024'")
            b_id = cursor.fetchone()["id"]

        client_auth = TestClient(app, cookies={"dogcu_access_token": token}, follow_redirects=False)
        update_res = client_auth.post(
            f"/admin/dogs/{b_id}/update",
            data={
                "name": "Bruno The Champion",
                "gender": "Male",
                "approx_age": "3.5 years",
                "description": "Beloved campus king and loyal companion.",
                "photo_url": "/static/images/bruno_portrait.jpg",
                "status_val": "ACTIVE",
                "health_status": "HEALTHY",
                "vaccination_status": "UP_TO_DATE",
                "sterilization_status": "YES",
                "health_notes": "All vaccines verified active.",
                "next_url": "/dog/CU-DOG-024",
            }
        )
        self.assertEqual(update_res.status_code, 303)
        self.assertIn("/dog/CU-DOG-024", update_res.headers["location"])

        # Verify change is live
        verify_res = fresh_client.get("/dog/CU-DOG-024")
        self.assertEqual(verify_res.status_code, 200)
        self.assertIn("BRUNO THE CHAMPION", verify_res.text)

    def test_28_admin_logout(self):
        """Logout clears the session cookie and redirects."""
        fresh_client = TestClient(app, follow_redirects=False)
        res = fresh_client.get("/admin/logout?next=/admin/login")
        self.assertEqual(res.status_code, 303)
        self.assertEqual(res.headers["location"], "/admin/login")
        set_cookie = res.headers.get("set-cookie", "")
        self.assertTrue("dogcu_access_token=\"\"" in set_cookie or "Max-Age=0" in set_cookie)

if __name__ == "__main__":
    unittest.main()

