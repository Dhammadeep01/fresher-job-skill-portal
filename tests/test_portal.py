import unittest
import os
import tempfile
import sqlite3
from app import create_app
from database import init_db, get_standalone_db
import matching_engine

class FresherPortalTestCase(unittest.TestCase):
    """
    Test Suite for Fresher Job and Skill Guidance Portal
    Validates Test Cases TC01 through TC10 defined in Mini Project Synopsis Section 4.5
    """

    def setUp(self):
        # Create a unique temporary database file for isolation
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.app = create_app({
            'TESTING': True,
            'DATABASE': self.db_path,
            'SECRET_KEY': 'test-secret-key'
        })
        self.client = self.app.test_client()
        
        # Initialize schema and seed data
        init_db(self.db_path, seed=True)

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    # ---------------------------------------------------------
    # TC01: Student Registration
    # Expected: Account created successfully; record saved in DB
    # ---------------------------------------------------------
    def test_tc01_student_registration(self):
        response = self.client.post('/register', data={
            'full_name': 'Aarav Sharma',
            'email': 'aarav.sharma@test.edu',
            'password': 'Password@123',
            'confirm_password': 'Password@123',
            'degree': 'MCA (Master of Computer Application)',
            'college': 'Mumbai University Dept of CS',
            'skills': 'Python, SQL, HTML, CSS',
            'target_role': 'Junior Python Developer'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)

        # Verify record in database
        conn = get_standalone_db(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, full_name, email, role FROM users WHERE email = ?", ('aarav.sharma@test.edu',))
        user = cur.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user['full_name'], 'Aarav Sharma')
        self.assertEqual(user['role'], 'student')
        conn.close()

    # ---------------------------------------------------------
    # TC02: Input Validation
    # Expected: Validation error displayed; record not saved
    # ---------------------------------------------------------
    def test_tc02_input_validation_missing_fields(self):
        # Submitting with empty email and mismatched passwords
        response = self.client.post('/register', data={
            'full_name': 'Incomplete User',
            'email': '',  # missing email
            'password': 'Secret123',
            'confirm_password': 'DifferentSecret456'
        }, follow_redirects=True)

        self.assertIn(b'Email address is required', response.data)

        # Confirm user was NOT created in DB
        conn = get_standalone_db(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE full_name = 'Incomplete User'")
        user = cur.fetchone()
        self.assertIsNone(user)
        conn.close()

    # ---------------------------------------------------------
    # TC03: Profile Management
    # Expected: Update candidate education and skill list successfully
    # ---------------------------------------------------------
    def test_tc03_profile_management(self):
        # Login as demo student (dhammadip@student.ac.in)
        self.client.post('/login', data={
            'email': 'dhammadip@student.ac.in',
            'password': 'Student@123'
        }, follow_redirects=True)

        # Update profile
        response = self.client.post('/student/profile', data={
            'degree': 'Master of Computer Application (MCA)',
            'field_of_study': 'Cloud & Full Stack Engineering',
            'college': 'Saket Gyanpeeth College',
            'graduation_year': '2026',
            'experience_level': 'Fresher (0 years)',
            'target_role': 'Full Stack Python Developer',
            'skills': 'Python, Flask, JavaScript, SQLite, Docker, Git, REST APIs',
            'bio': 'Final year MCA student focused on scalable web apps.'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your profile and skill records have been updated successfully', response.data)

        # Verify updated values in profile page
        profile_page = self.client.get('/student/profile')
        self.assertIn(b'Docker', profile_page.data)
        self.assertIn(b'Cloud &amp; Full Stack Engineering', profile_page.data)

    # ---------------------------------------------------------
    # TC04: Add Job Posting (Admin)
    # Expected: Job posting stored and published to job database
    # ---------------------------------------------------------
    def test_tc04_add_job_posting(self):
        # Login as administrator
        self.client.post('/login', data={
            'email': 'admin@fresherportal.com',
            'password': 'Admin@123'
        }, follow_redirects=True)

        response = self.client.post('/admin/jobs/create', data={
            'title': 'Junior Cloud Engineer',
            'company': 'NextGen Cloud Labs',
            'location': 'Mumbai, Maharashtra',
            'role_category': 'Cloud & DevOps',
            'job_type': 'Full-time',
            'education_req': 'B.Tech / MCA',
            'experience_req': 'Fresher',
            'required_skills': 'AWS, Linux, Python, Docker, Networking',
            'description': 'Entry-level cloud engineer to assist with AWS deployments and monitoring.',
            'responsibilities': 'Monitor cloud resources; write automation scripts in Python.',
            'eligibility_notes': 'Good problem solving skills.',
            'contact_email': 'jobs@nextgencloud.com'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'created successfully and published', response.data)

        # Verify stored in database
        conn = get_standalone_db(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM jobs WHERE title = 'Junior Cloud Engineer'")
        job = cur.fetchone()
        self.assertIsNotNone(job)
        self.assertEqual(job['company'], 'NextGen Cloud Labs')
        self.assertEqual(job['is_active'], 1)
        conn.close()

    # ---------------------------------------------------------
    # TC05: View Job Listings
    # Expected: Stored fresher job postings retrieved and displayed
    # ---------------------------------------------------------
    def test_tc05_view_job_listings(self):
        # Login as student
        self.client.post('/login', data={
            'email': 'dhammadip@student.ac.in',
            'password': 'Student@123'
        }, follow_redirects=True)

        response = self.client.get('/student/jobs')
        self.assertEqual(response.status_code, 200)
        # Should display seeded jobs
        self.assertIn(b'TechNova Solutions', response.data)
        self.assertIn(b'Apex Digital Labs', response.data)
        self.assertIn(b'ByteWave Innovations', response.data)

    # ---------------------------------------------------------
    # TC06: Job Matching Request
    # Expected: System returns matching jobs sorted by suitability
    # ---------------------------------------------------------
    def test_tc06_job_matching_request(self):
        # Candidate skills: Python, Flask, HTML5, CSS3, JavaScript, SQLite, Git
        cand_skills = 'Python, Flask, HTML5, CSS3, JavaScript, SQLite, Git'
        
        conn = get_standalone_db(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM jobs WHERE is_active = 1")
        all_jobs = cur.fetchall()
        
        ranked = matching_engine.rank_jobs_for_student(cand_skills, all_jobs, conn)
        conn.close()

        self.assertTrue(len(ranked) > 0)
        # Verify sorted descending by match score
        scores = [j['match_score'] for j in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))

    # ---------------------------------------------------------
    # TC07: Match Score Calculation
    # Scenario: Compare 4 candidate skills against 5 required job skills
    # Expected: Calculates exact 80% match score correctly
    # ---------------------------------------------------------
    def test_tc07_match_score_calculation(self):
        # Candidate has 4 of the 5 required skills
        candidate_skills = 'Python, SQL, REST APIs, Git'
        required_skills = 'Python, SQL, REST APIs, Git, Docker'  # 5 skills

        result = matching_engine.calculate_match(candidate_skills, required_skills)
        
        # (4 / 5) * 100 = 80%
        self.assertEqual(result['matched_count'], 4)
        self.assertEqual(result['total_required'], 5)
        self.assertEqual(result['match_score'], 80)
        self.assertEqual(result['match_level'], 'Strong Match')
        self.assertEqual(result['badge_class'], 'success')

    # ---------------------------------------------------------
    # TC08: Missing Skill Guidance
    # Expected: Evaluate missing job requirements against student profile
    #           and displays precise list of missing skills
    # ---------------------------------------------------------
    def test_tc08_missing_skill_guidance(self):
        candidate_skills = 'Python, SQL, Git'
        required_skills = 'Python, SQL, Git, Docker, REST APIs'

        result = matching_engine.calculate_match(candidate_skills, required_skills)
        self.assertIn('Docker', result['missing_skills'])
        self.assertIn('REST APIs', result['missing_skills'])

        conn = get_standalone_db(self.db_path)
        guidance = matching_engine.get_skill_guidance(result['missing_skills'], conn)
        conn.close()

        skill_names = [g['skill_name'] for g in guidance]
        self.assertIn('Docker', skill_names)
        self.assertIn('REST APIs', skill_names)

        # Check that resources and mini-projects are populated
        docker_item = next(g for g in guidance if g['skill_name'] == 'Docker')
        self.assertTrue(len(docker_item['resources']) > 0)
        self.assertIn('container', docker_item['mini_project'].lower())

    # ---------------------------------------------------------
    # TC09: Update Job Criteria (Admin)
    # Expected: Updated skill requirements reflect instantly in new match requests
    # ---------------------------------------------------------
    def test_tc09_update_job_criteria(self):
        # Seed student skills: Python, Flask, HTML5, CSS3, JavaScript, SQLite, Git
        cand_skills = 'Python, Flask, HTML5, CSS3, JavaScript, SQLite, Git'

        conn = get_standalone_db(self.db_path)
        cur = conn.cursor()
        # Find TechNova Solutions job (initially: Python, Flask, SQL, REST APIs, Git, Docker)
        cur.execute("SELECT id, required_skills FROM jobs WHERE company = 'TechNova Solutions'")
        job = cur.fetchone()
        job_id = job['id']
        conn.close()

        # Update skills to only 3 skills: Python, Flask, Git (which student fully has)
        self.client.post('/login', data={
            'email': 'admin@fresherportal.com',
            'password': 'Admin@123'
        }, follow_redirects=True)

        self.client.post(f'/admin/jobs/edit/{job_id}', data={
            'title': 'Junior Python / Backend Developer',
            'company': 'TechNova Solutions',
            'location': 'Mumbai, Maharashtra (Hybrid)',
            'role_category': 'Backend Development',
            'job_type': 'Full-time',
            'education_req': 'MCA / B.Tech',
            'experience_req': 'Fresher (0-1 year)',
            'required_skills': 'Python, Flask, Git',  # Now 3 skills that candidate has
            'description': 'Updated job description.',
            'responsibilities': 'Backend endpoints.',
            'eligibility_notes': 'All good.',
            'contact_email': 'careers@technova.com',
            'is_active': 'on'
        }, follow_redirects=True)

        # Check new match score for candidate: should be 100% now!
        conn2 = get_standalone_db(self.db_path)
        cur2 = conn2.cursor()
        cur2.execute("SELECT required_skills FROM jobs WHERE id = ?", (job_id,))
        updated_skills = cur2.fetchone()['required_skills']
        conn2.close()

        new_match = matching_engine.calculate_match(cand_skills, updated_skills)
        self.assertEqual(new_match['match_score'], 100)
        self.assertEqual(len(new_match['missing_skills']), 0)

    # ---------------------------------------------------------
    # TC10: Data Persistence
    # Expected: Restart Flask application server and reload portal ->
    #           All profiles and jobs remain available in SQLite
    # ---------------------------------------------------------
    def test_tc10_data_persistence(self):
        # 1. Insert a unique student profile
        conn = get_standalone_db(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (full_name, email, password_hash, role)
            VALUES ('Persistent Student', 'persist@test.edu', 'hash123', 'student')
        """)
        new_user_id = cur.lastrowid
        cur.execute("""
            INSERT INTO profiles (user_id, degree, college, skills)
            VALUES (?, 'MCA', 'Saket Gyanpeeth College', 'Python, Flask, SQLite')
        """, (new_user_id,))
        conn.commit()
        conn.close()

        # 2. Simulate server restart by creating a brand new Flask app instance pointing to same DB
        restarted_app = create_app({
            'TESTING': True,
            'DATABASE': self.db_path,
            'SECRET_KEY': 'new-session-key'
        })
        restarted_client = restarted_app.test_client()

        # 3. Verify user and profile still exist without data loss
        conn_check = get_standalone_db(self.db_path)
        cur_check = conn_check.cursor()
        cur_check.execute("SELECT * FROM users WHERE email = 'persist@test.edu'")
        persisted_user = cur_check.fetchone()
        self.assertIsNotNone(persisted_user)
        self.assertEqual(persisted_user['full_name'], 'Persistent Student')

        cur_check.execute("SELECT * FROM profiles WHERE user_id = ?", (persisted_user['id'],))
        persisted_profile = cur_check.fetchone()
        self.assertIsNotNone(persisted_profile)
        self.assertEqual(persisted_profile['skills'], 'Python, Flask, SQLite')
        conn_check.close()

if __name__ == '__main__':
    unittest.main()
