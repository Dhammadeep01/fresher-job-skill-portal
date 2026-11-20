-- Fresher Job and Skill Guidance Portal
-- SQLite Schema Definition

PRAGMA foreign_keys = ON;

-- Users Table (Students & Administrators)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student Profiles Table
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    degree TEXT DEFAULT '',
    field_of_study TEXT DEFAULT '',
    college TEXT DEFAULT '',
    graduation_year INTEGER DEFAULT 2026,
    experience_level TEXT DEFAULT 'Fresher (0 years)',
    target_role TEXT DEFAULT 'Software Developer',
    skills TEXT DEFAULT '',
    bio TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Jobs Listing Table (Managed by Admin)
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT NOT NULL,
    role_category TEXT NOT NULL,
    job_type TEXT DEFAULT 'Full-time',
    education_req TEXT NOT NULL,
    experience_req TEXT DEFAULT 'Fresher',
    required_skills TEXT NOT NULL,
    description TEXT NOT NULL,
    responsibilities TEXT DEFAULT '',
    eligibility_notes TEXT DEFAULT '',
    contact_email TEXT DEFAULT '',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Saved Jobs Table (Students can bookmark jobs)
CREATE TABLE IF NOT EXISTS saved_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
);

-- Curated Skill Guidance Knowledge Base
CREATE TABLE IF NOT EXISTS skill_guidance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT UNIQUE NOT NULL,
    category TEXT DEFAULT 'General',
    description TEXT NOT NULL,
    why_it_matters TEXT NOT NULL,
    recommended_resources TEXT NOT NULL,
    mini_project_idea TEXT NOT NULL,
    estimated_time TEXT DEFAULT '1-2 weeks'
);
