# FRESHER JOB AND SKILL GUIDANCE PORTAL
### A Web-Based Application — Mini Project Synopsis Implementation

**Candidate:** DHAMMADEEP HARSHABODH SHIRSATH (Roll No: 47)  
**Degree:** Master of Computer Application (MCA)  
**Guide:** Mrs. Sandhya Kapil Thakkar  
**Institution:** Saket Gyanpeeth College / Pramod Ram Ujagar Tiwari Saket Institute of Management  
**Affiliation:** University of Mumbai, Maharashtra  
**Academic Year:** 2026-2028  

---

## 1. Project Overview

Many fresh graduates complete their degree but face significant challenges identifying entry-level career opportunities aligned with their educational background and skill sets. Job listings are scattered, making it difficult for students to evaluate their eligibility or understand why they fail to qualify for specific positions.

The **Fresher Job & Skill Guidance Portal** solves this problem by providing:
1. **Centralized Job Catalog:** Focused exclusively on entry-level, trainee, and internship positions for fresh graduates.
2. **Transparent Rule-Based Matching Engine:** A deterministic algorithm calculating exact suitability percentages:
   $$\text{Match Score (\%)} = \left(\frac{\text{Matched Skills}}{\text{Total Required Skills}}\right) \times 100$$
3. **Structured Skill Gap Guidance:** Identifies missing technical competencies and provides tailored learning paths, curated free resources, and practical mini-project recommendations to bridge qualification gaps.
4. **Administrator Job Management:** Comprehensive interface for posting, updating, categorizing, and activating/deactivating fresher vacancies and skill criteria.

---

## 2. Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript (Responsive layout, custom CSS design system, interactive tag manager, real-time match meters)
- **Backend Framework:** Python 3 with Flask framework (3-Tier Architecture)
- **Database:** SQLite 3 (parameterized queries, relational foreign keys)
- **Authentication:** Werkzeug secure password hashing (PBKDF2-SHA256)
- **Testing:** Python `unittest` test suite covering test cases **TC01 through TC10**

---

## 3. Directory Structure & Root Map

```
fresher-job-skill-portal/
├── app.py                      # Flask Application Controller, Routes & Session Management
├── config.py                   # Central Application Configuration & Secrets
├── database.py                 # SQLite Connection Manager, Database Initialization & Seed Data
├── models.py                   # Data Access Layer with Parameterized SQL Queries
├── matching_engine.py          # Deterministic Rule-Based Job Matching & Skill Guidance Generator
├── schema.sql                  # Relational Database Schema Definitions (Users, Profiles, Jobs, Guidance)
├── fresher_portal.db           # Pre-seeded SQLite Database Instance
├── requirements.txt            # Python Dependencies (Flask, Werkzeug)
├── README.md                   # Complete Documentation, Root Map & User Guide
│
├── static/                     # Static UI Assets
│   ├── css/
│   │   ├── style.css           # Primary Design System (Typography, Components, Alerts, Tables, Badges)
│   │   └── dashboard.css       # Specialized Dashboard Styles, Metrics Cards, Match Meters
│   ├── js/
│   │   └── main.js             # Client Scripting (Interactive Skill Tags Input, Demo Autofill, Dismissals)
│   └── images/
│       └── logo.svg            # Custom SVG Portal Vector Brand Logo
│
├── templates/                  # Jinja2 HTML Templates
│   ├── base.html               # Master Layout (Navigation, User Badges, Flash Notifications, Footer)
│   ├── index.html              # Landing Page (Hero, System Stats, 3-Tier Workflow, Featured Openings)
│   ├── login.html              # Sign-In Page (with 1-Click Demo Credentials Autofill)
│   ├── register.html           # Student Registration Form with Form Validation
│   │
│   ├── student/                # Student Experience Views
│   │   ├── dashboard.html      # Student Dashboard (Profile Progress, Top Matches, In-Demand Gaps)
│   │   ├── profile.html        # Candidate Profile & Skill Editor (Interactive Tag Adder & Quick Skills)
│   │   ├── jobs.html           # Job Catalog with Category & Search Filters & Live Match Badges
│   │   ├── job_detail.html     # Detailed Job Breakdown, Match Formula Matrix & Missing Skill Guidance
│   │   ├── guidance.html       # Aggregated Skill Guidance Center (Roadmaps, Free Tutorials, Projects)
│   │   └── saved_jobs.html     # Bookmarked Jobs List with Current Suitability Scores
│   │
│   └── admin/                  # Administrator Management Views
│       ├── dashboard.html      # Admin Control Panel (System Metrics, Recent Jobs, Registered Students)
│       ├── manage_jobs.html    # Full Job Listings Management Table (Edit, Delete, Visibility Toggle)
│       ├── job_form.html       # Add / Edit Job Posting with Required Skill Tags & Criteria
│       └── students.html       # Registered Candidates Overview & Skill Inventory
│
└── tests/                      # Automated Verification Test Suite
    ├── __init__.py
    └── test_portal.py          # Automated Unit & Integration Tests (TC01 to TC10)
```

---

## 4. File-by-File Description

| File / Directory | Purpose & Key Responsibilities |
| :--- | :--- |
| `app.py` | Flask application factory. Defines public, student, and admin routing endpoints, authentication guards (`@login_required`, `@admin_required`, `@student_required`), session lifecycle, and error handling. |
| `config.py` | Central configuration containing `SECRET_KEY`, `DATABASE` file path, and cookie security flags. |
| `database.py` | Handles SQLite connection pooling, schema generation from `schema.sql`, and populates realistic initial data (Admin account, Student account, 8 fresher jobs, and 12 skill guidance knowledge records). |
| `models.py` | Structured Data Access Layer (DAL) employing parameterized SQL queries (`?`) to prevent SQL injection vulnerabilities across users, profiles, jobs, bookmarks, and admin metrics. |
| `matching_engine.py` | Core algorithmic matching module. Performs skill normalization, synonym resolution, computes exact percentage scores, extracts missing skills, and pairs them with curated learning paths. |
| `schema.sql` | DDL script defining tables: `users`, `profiles`, `jobs`, `saved_jobs`, and `skill_guidance` with foreign key integrity. |
| `static/css/style.css` | Comprehensive CSS design tokens (colors, buttons, badges, tables, alerts, responsive grid). |
| `static/css/dashboard.css` | Layout and card aesthetics for student and administrator dashboards, radial match indicators, and guidance cards. |
| `static/js/main.js` | Interactive frontend behaviors: multi-tag skill builder with removal pills, quick-add skill helpers, demo credential autofill, and alert dismissing. |
| `static/images/logo.svg` | Lightweight vector logo featuring a modern graduation cap and guidance star emblem. |
| `templates/base.html` | Root Jinja2 template featuring responsive navigation, role badges, notification toasts, and project attribution footer. |
| `templates/index.html` | Public portal showcase, metrics counters, how-it-works overview, and recent fresher vacancy preview cards. |
| `templates/student/*` | Student views: Dashboard, Profile Editor, Filterable Jobs Catalog, Match Formula Breakdown Card, Skill Guidance Center, and Bookmarked Jobs. |
| `templates/admin/*` | Administrator views: Dashboard with system statistics, Add/Edit Job Postings Form with skill tag picker, and Registered Student directory. |
| `tests/test_portal.py` | Automated test suite verifying test cases **TC01 through TC10** using an isolated temporary SQLite database. |

---

## 5. How to Run the Project

### Prerequisites
- Python 3.8 or higher installed on your computer.
- Python `Flask` and `Werkzeug` packages (already installed or installable via `pip install -r requirements.txt`).

### Step-by-Step Execution
1. Open your terminal or PowerShell and navigate to the project directory:
   ```powershell
   cd "C:\Users\dhammadeep\.gemini\antigravity\scratch\fresher-job-skill-portal"
   ```

2. (Optional) Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Launch the application:
   ```powershell
   python app.py
   ```

4. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 6. Pre-Configured Demo Credentials

For convenience during academic evaluation and testing, the portal includes pre-seeded accounts:

### 🎓 Student Account (Dhammadip Shirsath)
- **Email:** `dhammadip@student.ac.in`
- **Password:** `Student@123`
- **Pre-loaded Profile:** MCA candidate with skills in *Python, Flask, HTML5, CSS3, JavaScript, SQLite, Git*.
- *Tip: Click the "🎓 Fill Student" button on the login screen to autofill instantly!*

### ⚙️ Administrator Account
- **Email:** `admin@fresherportal.com`
- **Password:** `Admin@123`
- **Capabilities:** Create, edit, activate/deactivate, and delete fresher vacancies; update required skill criteria; view all registered candidates.
- *Tip: Click the "⚙️ Fill Admin" button on the login screen to autofill instantly!*

---

## 7. Automated Test Suite (TC01 to TC10)

To execute the automated verification test suite:

```powershell
python -m unittest discover -s tests -v
```

### Verified Test Cases:
- **TC01:** Student Registration with valid input details (Account successfully created).
- **TC02:** Input Validation for missing fields and mismatched passwords.
- **TC03:** Profile Management (Updating academic details and technical skill tags).
- **TC04:** Add Job Posting (Administrator creates vacancy with required skill tags).
- **TC05:** View Job Listings (Candidate retrieves active entry-level postings).
- **TC06:** Job Matching Request (Jobs sorted descending by suitability match).
- **TC07:** Match Score Calculation (Verifies exact **80%** match when 4 of 5 skills match).
- **TC08:** Missing Skill Guidance (Accurately itemizes missing skills with learning resources).
- **TC09:** Update Job Criteria (Admin edits skill requirements, reflecting instantly in candidate match scores).
- **TC10:** Data Persistence (Verification across application server reloads in SQLite).
