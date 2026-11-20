import sqlite3
import os
from flask import g, current_app
from werkzeug.security import generate_password_hash
from config import Config

def get_db():
    """Get database connection for current request context or standalone."""
    if 'db' not in g:
        db_path = current_app.config['DATABASE'] if current_app else Config.DATABASE
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def get_standalone_db(db_path=None):
    """Get a direct database connection outside Flask application context."""
    path = db_path or Config.DATABASE
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON;")
    return db

def close_db(e=None):
    """Close database connection at end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(db_path=None, seed=True):
    """Initialize database tables and seed sample data."""
    conn = get_standalone_db(db_path)
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    
    if seed:
        seed_initial_data(conn)
    
    conn.commit()
    conn.close()

def seed_initial_data(conn):
    """Seed administrator, demo student, fresher job listings, and skill knowledge base."""
    cursor = conn.cursor()
    
    # Check if admin already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", ('admin@fresherportal.com',))
    if cursor.fetchone():
        return  # Already seeded
    
    # 1. Admin Account
    admin_pw = generate_password_hash('Admin@123')
    cursor.execute("""
        INSERT INTO users (full_name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    """, ('System Administrator', 'admin@fresherportal.com', admin_pw, 'admin'))
    
    # 2. Demo Student Account (Dhammadip Harshabodh Shirsath)
    student_pw = generate_password_hash('Student@123')
    cursor.execute("""
        INSERT INTO users (full_name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    """, ('Dhammadip Shirsath', 'dhammadip@student.ac.in', student_pw, 'student'))
    student_user_id = cursor.lastrowid
    
    # Student Profile
    cursor.execute("""
        INSERT INTO profiles (
            user_id, degree, field_of_study, college, graduation_year,
            experience_level, target_role, skills, bio
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_user_id,
        'MCA (Master of Computer Application)',
        'Computer Applications & Software Engineering',
        'Saket Gyanpeeth College / Saket Institute of Management',
        2026,
        'Fresher (0 years)',
        'Junior Python / Backend Developer',
        'Python, Flask, HTML5, CSS3, JavaScript, SQLite, Git',
        'Final-year MCA student passionate about building full-stack web applications, backend APIs, and learning modern cloud technologies.'
    ))
    
    # 3. Seed Realistic Fresher Jobs
    jobs = [
        (
            'Junior Python / Backend Developer',
            'TechNova Solutions',
            'Mumbai, Maharashtra (Hybrid)',
            'Backend Development',
            'Full-time',
            'B.Sc / B.Tech / BCA / MCA in Computer Science or IT',
            'Fresher (0-1 year)',
            'Python, Flask, SQL, REST APIs, Git, Docker',
            'TechNova Solutions is looking for an enthusiastic Junior Python Developer. You will contribute to our core backend RESTful services, database optimization, and cloud deployments.',
            '• Design and implement backend endpoints using Python & Flask\n• Write clean, testable SQL queries and schema migrations\n• Collaborate with frontend developers to integrate client applications\n• Participate in code reviews and CI/CD pipelines',
            'Minimum 60% aggregate in graduation; MCA/B.Tech freshers eligible; Strong algorithmic problem solving',
            'careers@technovasolutions.in'
        ),
        (
            'Frontend Web Developer Trainee',
            'Apex Digital Labs',
            'Pune, Maharashtra (Remote)',
            'Frontend Development',
            'Full-time',
            'Any Graduate / BCA / MCA / B.E. Computer Engineering',
            'Fresher (0 years)',
            'HTML5, CSS3, JavaScript, React, Bootstrap, Git',
            'Join our UI/UX and web development cohort! Ideal for freshers who love crafting responsive, pixel-perfect user interfaces and interactive single-page applications.',
            '• Build responsive and cross-browser web interfaces using HTML5/CSS3 and React\n• Implement clean reusable UI component libraries\n• Integrate backend REST JSON APIs\n• Optimize web performance and load times',
            'Freshers from 2025/2026 batches welcome; Portfolio/GitHub projects preferred',
            'hr@apexdigitallabs.com'
        ),
        (
            'Associate Software Engineer (Core Development)',
            'Global Infoway Technologies',
            'Mumbai, Maharashtra (On-site)',
            'Software Engineering',
            'Full-time',
            'MCA / M.Sc CS / B.E. / B.Tech',
            'Fresher',
            'Java, Spring Boot, MySQL, OOP, Git, Agile',
            'Global Infoway is hiring fresh engineering graduates for enterprise software projects. Training will be provided during the initial 3 months of joining.',
            '• Participate in requirement analysis and object-oriented software design\n• Develop microservices and modules using Java and Spring Boot\n• Write unit tests with JUnit and Mockito\n• Maintain documentation and follow Agile sprint cadences',
            'Excellent understanding of OOP principles, data structures, and relational databases',
            'campus@globalinfoway.com'
        ),
        (
            'Junior Data Analyst',
            'Insight Analytics Corp',
            'Navi Mumbai, Maharashtra (Hybrid)',
            'Data & Analytics',
            'Full-time',
            'B.Sc Stats/Math/CS or BCA / MCA / B.Tech',
            'Fresher',
            'Python, SQL, Excel, Pandas, Data Visualization, PowerBI',
            'We are seeking a detail-oriented Junior Data Analyst to clean, analyze, and visualize business datasets, generating actionable business intelligence reports.',
            '• Extract, transform, and clean raw data using Python (Pandas) and SQL\n• Design interactive dashboards using PowerBI and Excel\n• Identify patterns, trends, and business KPI anomalies\n• Prepare executive summaries and visual charts',
            'Strong analytical thinking, solid SQL query skills, and willingness to learn cloud data warehousing',
            'talent@insightanalytics.com'
        ),
        (
            'Trainee QA & Test Automation Engineer',
            'QualityBridge Systems',
            'Mumbai, Maharashtra (On-site)',
            'Quality Assurance',
            'Full-time',
            'BCA / MCA / B.Sc CS / B.E.',
            'Fresher',
            'Python, Selenium, Manual Testing, SQL, JIRA, Test Automation',
            'Exciting opportunity for entry-level candidates aiming for a career in software quality assurance, automated test scripting, and bug tracking.',
            '• Write and execute test cases for web and API functionality\n• Automate regression suites using Python and Selenium WebDriver\n• Report bugs, verify fixes, and track issues in JIRA\n• Validate database consistency using SQL verification queries',
            'Good communication skills, attention to detail, and basic scripting knowledge',
            'jobs@qualitybridge.io'
        ),
        (
            'Cloud & DevOps Support Associate',
            'CloudScale Services',
            'Thane / Mumbai, Maharashtra (Hybrid)',
            'Cloud & DevOps',
            'Full-time',
            'B.Tech / MCA / B.Sc IT',
            'Fresher (0-1 year)',
            'Linux, Networking, AWS, Python, Bash, Troubleshooting',
            'Kickstart your cloud career with CloudScale. You will learn and assist in managing AWS infrastructure, server uptime, automation scripts, and monitoring.',
            '• Monitor server performance and cloud service alerts\n• Write shell scripts and Python automation for routine system tasks\n• Assist in deploying application releases via Docker and CI/CD pipelines\n• Troubleshoot network and Linux configuration issues',
            'Basic Linux command-line comfort; AWS Certified Cloud Practitioner is a plus but not mandatory',
            'careers@cloudscale.net'
        ),
        (
            'Full Stack Python Developer (Fresher)',
            'ByteWave Innovations',
            'Mumbai, Maharashtra (On-site)',
            'Full Stack Development',
            'Full-time',
            'MCA / B.E. / B.Tech / BCA',
            'Fresher',
            'Python, JavaScript, HTML5, CSS3, Flask, SQL, Git',
            'ByteWave is searching for a versatile fresher capable of working across both frontend web layouts and backend Python Flask logic for customer-facing portals.',
            '• Build dynamic end-to-end web features from HTML/CSS UI to Flask models\n• Implement user authentication, role-based access, and session management\n• Design normalized SQLite/PostgreSQL schemas and queries\n• Write clean, maintainable documentation and unit tests',
            'Candidates who have built academic or personal full-stack projects will be given top priority',
            'recruitment@bytewave.co'
        ),
        (
            'Junior Mobile App Developer (Flutter)',
            'AppCraft Studios',
            'Pune, Maharashtra (Hybrid)',
            'Mobile Development',
            'Full-time',
            'Any Graduate in Computer Science / IT / MCA',
            'Fresher',
            'Flutter, Dart, REST APIs, Git, Firebase, Mobile UI',
            'Create delightful cross-platform mobile apps for Android & iOS! You will work closely with senior mobile architects building consumer applications.',
            '• Develop mobile screens using Flutter and Dart framework\n• Connect apps to backend REST APIs and Firebase Firestore/Auth\n• Maintain clean state management using Provider / Riverpod / Bloc\n• Test and debug apps on physical devices and emulators',
            'Must have at least one sample Flutter project uploaded on GitHub or APK demo',
            'careers@appcraftstudios.in'
        )
    ]
    
    cursor.executemany("""
        INSERT INTO jobs (
            title, company, location, role_category, job_type, education_req,
            experience_req, required_skills, description, responsibilities,
            eligibility_notes, contact_email
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, jobs)
    
    # 4. Seed Curated Skill Guidance Knowledge Base
    guidance_items = [
        (
            'Docker',
            'DevOps & Deployment',
            'Docker is a containerization platform that packages applications and their dependencies into lightweight, isolated containers for consistent execution across environments.',
            'Modern cloud architectures and enterprise teams rely on Docker for reproducible development, testing, and deployment without "it works on my machine" issues.',
            '• Docker Official 101 Tutorial (docs.docker.com)\n• freeCodeCamp Docker for Beginners on YouTube\n• Play with Docker (labs.play-with-docker.com)',
            'Containerize your current Flask + SQLite application by creating a Dockerfile and docker-compose.yml file, and running it locally in a container.',
            '1-2 weeks'
        ),
        (
            'REST APIs',
            'Backend Engineering',
            'REST (Representational State Transfer) is the architectural standard for exchanging data between client applications (web/mobile) and backend servers using HTTP methods.',
            'Almost every modern web and mobile application communicates via RESTful JSON endpoints. Mastery of status codes, serialization, and routing is fundamental for backend freshers.',
            '• MDN Web Docs: Working with REST APIs\n• Flask-RESTful & Flask jsonify official documentation\n• Postman API fundamentals learning path',
            'Build a mini REST API in Flask for a Books or Student library with full CRUD (GET, POST, PUT, DELETE) endpoints and test them using Postman.',
            '3-5 days'
        ),
        (
            'React',
            'Frontend Engineering',
            'React is a widely adopted declarative, component-based JavaScript library developed by Meta for building dynamic and interactive single-page user interfaces.',
            'React dominates industry frontend development. Knowing components, props, hooks (useState, useEffect), and virtual DOM will dramatically boost fresher hiring chances.',
            '• Official React Documentation (react.dev)\n• Scrimba Free Interactive React Course\n• FullStackOpen (University of Helsinki free course)',
            'Build a responsive Task / To-Do Tracker in React that consumes an external REST API or localStorage with filter by status and search capability.',
            '2-3 weeks'
        ),
        (
            'Bootstrap',
            'Frontend UI',
            'Bootstrap is the most popular open-source CSS framework featuring a responsive 12-column grid system, pre-styled UI components, and utility classes.',
            'Accelerates responsive UI development without having to write hundreds of lines of custom media queries from scratch.',
            '• GetBootstrap.com official documentation and component examples\n• W3Schools Bootstrap 5 interactive tutorial',
            'Convert a static webpage into a mobile-friendly responsive landing page using Bootstrap 5 grid, navbar, modal, and card components.',
            '3-5 days'
        ),
        (
            'Java',
            'Core Programming',
            'Java is a versatile, object-oriented, cross-platform programming language widely utilized in enterprise software systems, banking, and backend backbones.',
            'Top IT recruiters and MNCs heavily conduct campus drives testing Java OOP concepts, collections framework, exception handling, and multithreading.',
            '• Oracle Java SE Tutorials\n• Java Programming Mooc.fi (University of Helsinki)\n• GeeksforGeeks Java collection & OOP guides',
            'Create a console or GUI-based Student Management System in Java implementing inheritance, encapsulation, file I/O, and custom exceptions.',
            '2-3 weeks'
        ),
        (
            'Spring Boot',
            'Enterprise Backend',
            'Spring Boot is an opinionated, production-ready framework for Java that simplifies microservice and enterprise REST API creation with auto-configuration.',
            'Most Java enterprise jobs require Spring Boot for microservices, JPA/Hibernate persistence, and dependency injection.',
            '• Spring.io Quickstart Guide\n• Baeldung Spring Boot Tutorials\n• Amigoscode Spring Boot YouTube Crash Course',
            'Develop an employee directory API using Spring Boot, Spring Data JPA, and H2/MySQL database with basic validation.',
            '2-3 weeks'
        ),
        (
            'Pandas',
            'Data Science & Analytics',
            'Pandas is a fast, powerful, and flexible Python data analysis and manipulation library built on top of NumPy, centered around DataFrame objects.',
            'It is the foundational industry standard tool for data cleaning, aggregation, exploratory data analysis (EDA), and tabular data processing.',
            '• 10 Minutes to pandas official tutorial\n• Kaggle: Pandas micro-course (free certification)\n• Corey Schafer Pandas YouTube series',
            'Download a Kaggle dataset (e.g. Titanic or Job Market dataset), clean missing values, group data by categories, and compute summary statistics.',
            '1 week'
        ),
        (
            'PowerBI',
            'Business Intelligence',
            'Microsoft PowerBI is a business analytics and visual dashboarding tool that turns unrelated data sources into coherent, interactive, and visually immersive insights.',
            'Highly demanded across business analytics, corporate reporting, and management consulting roles for executive dashboards.',
            '• Microsoft Learn: Power BI beginner path\n• Guy in a Cube YouTube channel\n• Free Power BI Desktop download & tutorials',
            'Import an Excel/CSV sales or student placement dataset into PowerBI Desktop, model relationships, and build a 1-page interactive dashboard with slicers and KPI cards.',
            '1-2 weeks'
        ),
        (
            'Selenium',
            'Test Automation',
            'Selenium is an open-source test automation framework used to validate web applications across different browsers and platforms.',
            'QA fresher roles prioritize candidates who can write automated browser test scripts instead of purely performing repetitive manual tests.',
            '• Selenium.dev official documentation\n• Test Automation University: Web Element Locator & Selenium Python\n• Rahul Shetty Academy YouTube previews',
            'Write a Python script using Selenium WebDriver to automatically open a login page, type credentials, submit the form, and assert that the dashboard loads.',
            '1-2 weeks'
        ),
        (
            'AWS',
            'Cloud Computing',
            'Amazon Web Services (AWS) is the world’s most comprehensive and broadly adopted cloud platform, offering services like EC2, S3, RDS, and Lambda.',
            'Companies host their production services on the cloud. Understanding compute instances, cloud storage, and security groups provides a huge competitive edge.',
            '• AWS Skill Builder free digital training\n• AWS Free Tier account hands-on experiments\n• freeCodeCamp AWS Cloud Practitioner Exam Prep',
            'Launch a free-tier Ubuntu EC2 instance on AWS, SSH into it, install Python/Flask, and deploy your live web application.',
            '2 weeks'
        ),
        (
            'Linux',
            'Operating Systems & Infrastructure',
            'Linux is an open-source Unix-like operating system powering over 90% of cloud servers, containers, and internet infrastructure.',
            'Basic Linux command line proficiency (file navigation, permissions, process management, SSH) is essential for any backend, cloud, or DevOps role.',
            '• Linux Journey (linuxjourney.com)\n• OverTheWire Bandit wargame (gamified Linux CLI learning)\n• MDN / Red Hat Command Line basics',
            'Set up WSL2 (Windows Subsystem for Linux) or a virtual machine, and manage user accounts, file permissions (chmod/chown), and system services (systemctl).',
            '1 week'
        ),
        (
            'Flutter',
            'Mobile Development',
            'Flutter is Google’s UI toolkit for building natively compiled applications for mobile, web, and desktop from a single codebase using the Dart language.',
            'Allows building high-performance iOS and Android applications with hot reload, beautiful widgets, and faster development cycles.',
            '• Flutter.dev official documentation and codelabs\n• Flutter & Dart Complete Guide on YouTube\n• Flutter Gallery showcase app',
            'Create a multi-screen mobile Recipe or Note Taking app with SQLite/Hive local storage and custom themed widgets.',
            '2-3 weeks'
        )
    ]
    
    cursor.executemany("""
        INSERT INTO skill_guidance (
            skill_name, category, description, why_it_matters,
            recommended_resources, mini_project_idea, estimated_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, guidance_items)
