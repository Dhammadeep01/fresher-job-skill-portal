import sqlite3
from database import get_db

# -------------------------------------------------------------
# User Account Operations
# -------------------------------------------------------------

def get_user_by_id(user_id):
    """Retrieve user record by primary key ID."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

def get_user_by_email(email):
    """Retrieve user record by unique email address."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
    return cursor.fetchone()

def create_user(full_name, email, password_hash, role='student'):
    """Insert a new user record and initialize an empty student profile if role is student."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO users (full_name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    """, (full_name.strip(), email.strip().lower(), password_hash, role))
    user_id = cursor.lastrowid
    
    if role == 'student':
        cursor.execute("""
            INSERT INTO profiles (user_id, degree, field_of_study, college, graduation_year, experience_level, target_role, skills, bio)
            VALUES (?, '', '', '', 2026, 'Fresher (0 years)', 'Software Developer', '', '')
        """, (user_id,))
        
    db.commit()
    return user_id

def get_all_students():
    """Retrieve all student accounts joined with their profile data."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT u.id, u.full_name, u.email, u.created_at,
               p.degree, p.college, p.skills, p.target_role, p.experience_level
        FROM users u
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE u.role = 'student'
        ORDER BY u.id DESC
    """)
    return cursor.fetchall()

# -------------------------------------------------------------
# Student Profile Operations
# -------------------------------------------------------------

def get_student_profile(user_id):
    """Fetch complete profile record for a given user ID."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.*, u.full_name, u.email
        FROM profiles p
        JOIN users u ON p.user_id = u.id
        WHERE p.user_id = ?
    """, (user_id,))
    profile = cursor.fetchone()
    if not profile:
        # Create empty profile if missing
        cursor.execute("INSERT OR IGNORE INTO profiles (user_id) VALUES (?)", (user_id,))
        db.commit()
        cursor.execute("""
            SELECT p.*, u.full_name, u.email
            FROM profiles p
            JOIN users u ON p.user_id = u.id
            WHERE p.user_id = ?
        """, (user_id,))
        profile = cursor.fetchone()
    return profile

def update_student_profile(user_id, degree, field_of_study, college, graduation_year, experience_level, target_role, skills, bio):
    """Update profile fields using parameterized SQL query."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE profiles
        SET degree = ?,
            field_of_study = ?,
            college = ?,
            graduation_year = ?,
            experience_level = ?,
            target_role = ?,
            skills = ?,
            bio = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    """, (
        degree.strip(),
        field_of_study.strip(),
        college.strip(),
        int(graduation_year) if str(graduation_year).isdigit() else 2026,
        experience_level.strip(),
        target_role.strip(),
        skills.strip(),
        bio.strip(),
        user_id
    ))
    db.commit()
    return cursor.rowcount > 0

# -------------------------------------------------------------
# Job Postings Operations (Admin & Student Views)
# -------------------------------------------------------------

def get_all_jobs(active_only=True, category=None, search=None):
    """
    Query job listings with optional filtering by active status, category, or search term.
    """
    db = get_db()
    cursor = db.cursor()
    
    conditions = []
    params = []
    
    if active_only:
        conditions.append("is_active = 1")
        
    if category and category != 'All':
        conditions.append("role_category = ?")
        params.append(category)
        
    if search:
        search_pattern = f"%{search.strip()}%"
        conditions.append("(title LIKE ? OR company LIKE ? OR required_skills LIKE ? OR location LIKE ?)")
        params.extend([search_pattern, search_pattern, search_pattern, search_pattern])
        
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
        SELECT * FROM jobs
        {where_clause}
        ORDER BY id DESC
    """
    cursor.execute(query, params)
    return cursor.fetchall()

def get_job_by_id(job_id):
    """Fetch a single job posting by ID."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    return cursor.fetchone()

def create_job(data):
    """Create a new job posting."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO jobs (
            title, company, location, role_category, job_type, education_req,
            experience_req, required_skills, description, responsibilities,
            eligibility_notes, contact_email, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('title', '').strip(),
        data.get('company', '').strip(),
        data.get('location', '').strip(),
        data.get('role_category', 'General IT').strip(),
        data.get('job_type', 'Full-time').strip(),
        data.get('education_req', '').strip(),
        data.get('experience_req', 'Fresher').strip(),
        data.get('required_skills', '').strip(),
        data.get('description', '').strip(),
        data.get('responsibilities', '').strip(),
        data.get('eligibility_notes', '').strip(),
        data.get('contact_email', '').strip(),
        1 if data.get('is_active', 1) else 0
    ))
    db.commit()
    return cursor.lastrowid

def update_job(job_id, data):
    """Update existing job details and required skill tags."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE jobs
        SET title = ?,
            company = ?,
            location = ?,
            role_category = ?,
            job_type = ?,
            education_req = ?,
            experience_req = ?,
            required_skills = ?,
            description = ?,
            responsibilities = ?,
            eligibility_notes = ?,
            contact_email = ?,
            is_active = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        data.get('title', '').strip(),
        data.get('company', '').strip(),
        data.get('location', '').strip(),
        data.get('role_category', '').strip(),
        data.get('job_type', 'Full-time').strip(),
        data.get('education_req', '').strip(),
        data.get('experience_req', 'Fresher').strip(),
        data.get('required_skills', '').strip(),
        data.get('description', '').strip(),
        data.get('responsibilities', '').strip(),
        data.get('eligibility_notes', '').strip(),
        data.get('contact_email', '').strip(),
        1 if data.get('is_active', 1) else 0,
        job_id
    ))
    db.commit()
    return cursor.rowcount > 0

def delete_job(job_id):
    """Delete a job posting."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    db.commit()
    return cursor.rowcount > 0

def toggle_job_status(job_id):
    """Toggle job between active and inactive status."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE jobs SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?", (job_id,))
    db.commit()
    return cursor.rowcount > 0

# -------------------------------------------------------------
# Saved Jobs (Bookmarking)
# -------------------------------------------------------------

def is_job_saved(user_id, job_id):
    """Check if a student has saved/bookmarked this job."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM saved_jobs WHERE user_id = ? AND job_id = ?", (user_id, job_id))
    return cursor.fetchone() is not None

def toggle_saved_job(user_id, job_id):
    """Add or remove a job from student's saved list."""
    db = get_db()
    cursor = db.cursor()
    if is_job_saved(user_id, job_id):
        cursor.execute("DELETE FROM saved_jobs WHERE user_id = ? AND job_id = ?", (user_id, job_id))
        saved = False
    else:
        cursor.execute("INSERT INTO saved_jobs (user_id, job_id) VALUES (?, ?)", (user_id, job_id))
        saved = True
    db.commit()
    return saved

def get_saved_jobs(user_id):
    """Retrieve all jobs bookmarked by a student."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT j.*, s.saved_at
        FROM saved_jobs s
        JOIN jobs j ON s.job_id = j.id
        WHERE s.user_id = ?
        ORDER BY s.saved_at DESC
    """, (user_id,))
    return cursor.fetchall()

# -------------------------------------------------------------
# Portal Statistics (Admin Dashboard)
# -------------------------------------------------------------

def get_admin_metrics():
    """Compute aggregate numbers for the administrator dashboard."""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_active = 1")
    active_jobs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
    total_students = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM saved_jobs")
    total_bookmarks = cursor.fetchone()[0]
    
    # Get distinct role categories
    cursor.execute("SELECT DISTINCT role_category FROM jobs")
    categories = [r[0] for r in cursor.fetchall() if r[0]]
    
    return {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_students': total_students,
        'total_bookmarks': total_bookmarks,
        'categories_count': len(categories)
    }
