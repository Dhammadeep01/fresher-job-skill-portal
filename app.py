import os
import functools
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, g, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from database import get_db, close_db, init_db
import models
import matching_engine

def create_app(test_config=None):
    """Application factory for Fresher Job and Skill Guidance Portal."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    # Register database teardown
    app.teardown_appcontext(close_db)

    # Initialize database if it does not exist
    db_path = app.config['DATABASE']
    if not os.path.exists(db_path):
        with app.app_context():
            init_db(db_path, seed=True)

    # ---------------------------------------------------------
    # Context Processor & Auth Helpers
    # ---------------------------------------------------------
    @app.context_processor
    def inject_user():
        user_id = session.get('user_id')
        user = None
        if user_id:
            user = models.get_user_by_id(user_id)
        return dict(
            current_user=user,
            is_authenticated=(user is not None),
            is_admin=(user and user['role'] == 'admin'),
            is_student=(user and user['role'] == 'student')
        )

    def login_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if not session.get('user_id'):
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login', next=request.path))
            return view(**kwargs)
        return wrapped_view

    def admin_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            user_id = session.get('user_id')
            if not user_id:
                flash('Administrator login required.', 'warning')
                return redirect(url_for('login', next=request.path))
            user = models.get_user_by_id(user_id)
            if not user or user['role'] != 'admin':
                flash('Access denied. Administrator privileges required.', 'danger')
                return redirect(url_for('index'))
            return view(**kwargs)
        return wrapped_view

    def student_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            user_id = session.get('user_id')
            if not user_id:
                flash('Please log in as a student to access this page.', 'warning')
                return redirect(url_for('login', next=request.path))
            user = models.get_user_by_id(user_id)
            if not user or user['role'] != 'student':
                flash('Access denied. Student account required.', 'danger')
                return redirect(url_for('index'))
            return view(**kwargs)
        return wrapped_view

    # ---------------------------------------------------------
    # Public & Authentication Routes
    # ---------------------------------------------------------
    @app.route('/')
    def index():
        """Home / Landing page showcasing portal features and project synopsis info."""
        jobs = models.get_all_jobs(active_only=True)
        stats = models.get_admin_metrics()
        
        # If student is logged in, calculate match score preview for featured jobs
        user_id = session.get('user_id')
        scored_jobs = []
        if user_id and session.get('role') == 'student':
            profile = models.get_student_profile(user_id)
            cand_skills = profile['skills'] if profile else ''
            scored_jobs = matching_engine.rank_jobs_for_student(cand_skills, jobs[:6], get_db())
        else:
            scored_jobs = [dict(j) for j in jobs[:6]]

        return render_template('index.html', stats=stats, featured_jobs=scored_jobs)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Student registration endpoint (TC01, TC02)."""
        if session.get('user_id'):
            return redirect(url_for('student_dashboard' if session.get('role') == 'student' else 'admin_dashboard'))

        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            degree = request.form.get('degree', '').strip()
            college = request.form.get('college', '').strip()
            initial_skills = request.form.get('skills', '').strip()
            target_role = request.form.get('target_role', 'Software Developer').strip()

            # TC02: Input validation
            errors = []
            if not full_name:
                errors.append('Full Name is required.')
            if not email:
                errors.append('Email address is required.')
            elif '@' not in email or '.' not in email:
                errors.append('Please provide a valid email address.')
            if not password:
                errors.append('Password is required.')
            elif len(password) < 6:
                errors.append('Password must be at least 6 characters long.')
            if password != confirm_password:
                errors.append('Passwords do not match.')

            if not errors:
                existing = models.get_user_by_email(email)
                if existing:
                    errors.append('An account with this email address already exists.')

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template(
                    'register.html',
                    form_data=request.form,
                    title='Student Registration'
                )

            # TC01: Create user record
            pw_hash = generate_password_hash(password)
            user_id = models.create_user(full_name, email, pw_hash, role='student')

            # Update student profile with initial info if provided
            if degree or college or initial_skills:
                models.update_student_profile(
                    user_id=user_id,
                    degree=degree or 'MCA',
                    field_of_study='Computer Application / IT',
                    college=college or 'Saket Gyanpeeth College',
                    graduation_year=2026,
                    experience_level='Fresher (0 years)',
                    target_role=target_role or 'Junior Software Engineer',
                    skills=initial_skills,
                    bio=''
                )

            session.clear()
            session['user_id'] = user_id
            session['user_name'] = full_name
            session['role'] = 'student'

            flash(f'Registration successful! Welcome to the portal, {full_name}.', 'success')
            return redirect(url_for('student_profile'))

        return render_template('register.html', title='Student Registration')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login for both students and administrators."""
        if session.get('user_id'):
            return redirect(url_for('student_dashboard' if session.get('role') == 'student' else 'admin_dashboard'))

        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')

            if not email or not password:
                flash('Please enter both email and password.', 'warning')
                return render_template('login.html', email=email, title='Sign In')

            user = models.get_user_by_email(email)
            if not user or not check_password_hash(user['password_hash'], password):
                flash('Invalid email or password. Please check your credentials.', 'danger')
                return render_template('login.html', email=email, title='Sign In')

            # Establish session
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['role'] = user['role']

            flash(f'Welcome back, {user["full_name"]}!', 'success')

            # Role-based redirect
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('student_dashboard'))

        return render_template('login.html', title='Sign In')

    @app.route('/logout')
    def logout():
        """Log out user and clear session."""
        session.clear()
        flash('You have been safely logged out.', 'info')
        return redirect(url_for('login'))

    # ---------------------------------------------------------
    # Student Module Routes
    # ---------------------------------------------------------
    @app.route('/student/dashboard')
    @student_required
    def student_dashboard():
        """Student dashboard with profile completion, top matching jobs, and missing skill highlights."""
        user_id = session['user_id']
        profile = models.get_student_profile(user_id)
        all_jobs = models.get_all_jobs(active_only=True)

        cand_skills = profile['skills'] if profile else ''
        ranked_jobs = matching_engine.rank_jobs_for_student(cand_skills, all_jobs, get_db())

        # Top 3 matches
        top_matches = ranked_jobs[:3]

        # Calculate student profile completeness
        fields = [profile['degree'], profile['college'], profile['skills'], profile['target_role'], profile['bio']]
        filled_fields = sum(1 for f in fields if f and str(f).strip())
        profile_completeness = int((filled_fields / len(fields)) * 100)

        # High match count
        high_matches = sum(1 for j in ranked_jobs if j['match_score'] >= 80)
        moderate_matches = sum(1 for j in ranked_jobs if 50 <= j['match_score'] < 80)

        # Aggregate top missing skills across all jobs
        missing_skills_counter = {}
        for j in ranked_jobs:
            for skill in j.get('missing_skills', []):
                norm = skill.strip().title()
                missing_skills_counter[norm] = missing_skills_counter.get(norm, 0) + 1

        top_missing_skills = sorted(missing_skills_counter.items(), key=lambda x: x[1], reverse=True)[:5]

        return render_template(
            'student/dashboard.html',
            profile=profile,
            top_matches=top_matches,
            total_jobs_count=len(all_jobs),
            high_matches=high_matches,
            moderate_matches=moderate_matches,
            profile_completeness=profile_completeness,
            top_missing_skills=top_missing_skills,
            parsed_skills=matching_engine.parse_skills(cand_skills),
            title='Student Dashboard'
        )

    @app.route('/student/profile', methods=['GET', 'POST'])
    @student_required
    def student_profile():
        """View and update student education and skill profile (TC03)."""
        user_id = session['user_id']
        profile = models.get_student_profile(user_id)

        if request.method == 'POST':
            degree = request.form.get('degree', '').strip()
            field_of_study = request.form.get('field_of_study', '').strip()
            college = request.form.get('college', '').strip()
            graduation_year = request.form.get('graduation_year', '2026').strip()
            experience_level = request.form.get('experience_level', 'Fresher (0 years)').strip()
            target_role = request.form.get('target_role', '').strip()
            skills = request.form.get('skills', '').strip()
            bio = request.form.get('bio', '').strip()

            models.update_student_profile(
                user_id=user_id,
                degree=degree,
                field_of_study=field_of_study,
                college=college,
                graduation_year=graduation_year,
                experience_level=experience_level,
                target_role=target_role,
                skills=skills,
                bio=bio
            )

            flash('Your profile and skill records have been updated successfully!', 'success')
            return redirect(url_for('student_profile'))

        parsed_skills = matching_engine.parse_skills(profile['skills'] if profile else '')
        return render_template(
            'student/profile.html',
            profile=profile,
            parsed_skills=parsed_skills,
            title='My Profile'
        )

    @app.route('/student/jobs')
    @student_required
    def student_jobs():
        """Browse fresher jobs with transparent rule-based matching scores (TC05, TC06)."""
        user_id = session['user_id']
        profile = models.get_student_profile(user_id)
        cand_skills = profile['skills'] if profile else ''

        category_filter = request.args.get('category', 'All')
        search_query = request.args.get('q', '').strip()
        sort_by = request.args.get('sort', 'match')  # 'match' or 'recent'

        all_jobs = models.get_all_jobs(
            active_only=True,
            category=category_filter if category_filter != 'All' else None,
            search=search_query if search_query else None
        )

        ranked_jobs = matching_engine.rank_jobs_for_student(cand_skills, all_jobs, get_db())

        if sort_by == 'recent':
            ranked_jobs.sort(key=lambda x: x.get('id', 0), reverse=True)

        # Get unique categories for filter dropdown
        categories = ['All', 'Backend Development', 'Frontend Development', 'Software Engineering',
                      'Data & Analytics', 'Quality Assurance', 'Cloud & DevOps', 'Full Stack Development', 'Mobile Development']

        return render_template(
            'student/jobs.html',
            jobs=ranked_jobs,
            categories=categories,
            selected_category=category_filter,
            search_query=search_query,
            sort_by=sort_by,
            cand_skills=cand_skills,
            title='Fresher Job Listings & Match Scores'
        )

    @app.route('/student/job/<int:job_id>')
    @student_required
    def student_job_detail(job_id):
        """
        Job details view with detailed rule-based matching calculation and
        missing skill guidance (TC07, TC08).
        """
        user_id = session['user_id']
        job = models.get_job_by_id(job_id)
        if not job:
            flash('Job posting not found.', 'danger')
            return redirect(url_for('student_jobs'))

        profile = models.get_student_profile(user_id)
        cand_skills = profile['skills'] if profile else ''

        # Execute rule-based matching
        match_info = matching_engine.calculate_match(cand_skills, job['required_skills'])
        # Retrieve missing skill guidance
        guidance = matching_engine.get_skill_guidance(match_info['missing_skills'], get_db())

        is_saved = models.is_job_saved(user_id, job_id)

        return render_template(
            'student/job_detail.html',
            job=job,
            match=match_info,
            guidance=guidance,
            is_saved=is_saved,
            cand_skills_list=matching_engine.parse_skills(cand_skills),
            req_skills_list=matching_engine.parse_skills(job['required_skills']),
            title=f"{job['title']} - Match & Skill Guidance"
        )

    @app.route('/student/guidance')
    @student_required
    def student_skill_guidance():
        """
        Comprehensive Skill Guidance Center:
        Aggregates missing skills across all jobs or target role and delivers learning pathways.
        """
        user_id = session['user_id']
        profile = models.get_student_profile(user_id)
        cand_skills = profile['skills'] if profile else ''
        all_jobs = models.get_all_jobs(active_only=True)

        ranked_jobs = matching_engine.rank_jobs_for_student(cand_skills, all_jobs, get_db())

        # Collect all unique missing skills across target role / top jobs
        missing_frequency = {}
        for j in ranked_jobs:
            for s in j.get('missing_skills', []):
                norm = s.strip().title()
                missing_frequency[norm] = missing_frequency.get(norm, 0) + 1

        sorted_missing = [s for s, count in sorted(missing_frequency.items(), key=lambda x: x[1], reverse=True)]
        guidance_items = matching_engine.get_skill_guidance(sorted_missing, get_db())

        # Attach demand frequency to guidance
        for g_item in guidance_items:
            g_item['demand_count'] = missing_frequency.get(g_item['skill_name'].strip().title(), 1)

        return render_template(
            'student/guidance.html',
            profile=profile,
            guidance_items=guidance_items,
            cand_skills_list=matching_engine.parse_skills(cand_skills),
            title='Missing Skill Guidance & Learning Paths'
        )

    @app.route('/student/save-job/<int:job_id>', methods=['POST'])
    @student_required
    def student_toggle_save_job(job_id):
        """Toggle bookmark for a job."""
        user_id = session['user_id']
        saved = models.toggle_saved_job(user_id, job_id)
        if saved:
            flash('Job bookmarked to your saved list.', 'success')
        else:
            flash('Job removed from your saved list.', 'info')
        return redirect(request.referrer or url_for('student_jobs'))

    @app.route('/student/saved-jobs')
    @student_required
    def student_saved_jobs():
        """View saved/bookmarked jobs."""
        user_id = session['user_id']
        profile = models.get_student_profile(user_id)
        cand_skills = profile['skills'] if profile else ''

        saved_records = models.get_saved_jobs(user_id)
        ranked_saved = matching_engine.rank_jobs_for_student(cand_skills, saved_records, get_db())

        return render_template(
            'student/saved_jobs.html',
            jobs=ranked_saved,
            title='Saved Job Bookmarks'
        )

    # ---------------------------------------------------------
    # Administrator Module Routes
    # ---------------------------------------------------------
    @app.route('/admin/dashboard')
    @admin_required
    def admin_dashboard():
        """Admin dashboard with system statistics and job management table."""
        stats = models.get_admin_metrics()
        jobs = models.get_all_jobs(active_only=False)
        students = models.get_all_students()

        return render_template(
            'admin/dashboard.html',
            stats=stats,
            jobs=jobs[:8],
            students=students[:5],
            title='Admin Dashboard'
        )

    @app.route('/admin/jobs')
    @admin_required
    def admin_manage_jobs():
        """List and manage all job postings (active and inactive)."""
        jobs = models.get_all_jobs(active_only=False)
        return render_template('admin/manage_jobs.html', jobs=jobs, title='Manage Job Postings')

    @app.route('/admin/jobs/create', methods=['GET', 'POST'])
    @admin_required
    def admin_create_job():
        """Create a new job posting with skill criteria (TC04)."""
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            company = request.form.get('company', '').strip()
            location = request.form.get('location', '').strip()
            role_category = request.form.get('role_category', 'General IT').strip()
            job_type = request.form.get('job_type', 'Full-time').strip()
            education_req = request.form.get('education_req', '').strip()
            experience_req = request.form.get('experience_req', 'Fresher').strip()
            required_skills = request.form.get('required_skills', '').strip()
            description = request.form.get('description', '').strip()
            responsibilities = request.form.get('responsibilities', '').strip()
            eligibility_notes = request.form.get('eligibility_notes', '').strip()
            contact_email = request.form.get('contact_email', '').strip()

            errors = []
            if not title:
                errors.append('Job Title is required.')
            if not company:
                errors.append('Company Name is required.')
            if not required_skills:
                errors.append('Required Skills list is required for the matching algorithm.')
            if not description:
                errors.append('Job Description is required.')

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('admin/job_form.html', form_data=request.form, is_edit=False, title='Add New Job Posting')

            job_id = models.create_job({
                'title': title,
                'company': company,
                'location': location or 'Mumbai / Remote',
                'role_category': role_category,
                'job_type': job_type,
                'education_req': education_req or 'B.Tech / MCA / B.Sc CS',
                'experience_req': experience_req,
                'required_skills': required_skills,
                'description': description,
                'responsibilities': responsibilities,
                'eligibility_notes': eligibility_notes,
                'contact_email': contact_email,
                'is_active': 1
            })

            flash(f'Job posting "{title}" created successfully and published to portal!', 'success')
            return redirect(url_for('admin_manage_jobs'))

        return render_template('admin/job_form.html', form_data={}, is_edit=False, title='Add New Job Posting')

    @app.route('/admin/jobs/edit/<int:job_id>', methods=['GET', 'POST'])
    @admin_required
    def admin_edit_job(job_id):
        """Edit job posting and required skills (TC09)."""
        job = models.get_job_by_id(job_id)
        if not job:
            flash('Job posting not found.', 'danger')
            return redirect(url_for('admin_manage_jobs'))

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            company = request.form.get('company', '').strip()
            location = request.form.get('location', '').strip()
            role_category = request.form.get('role_category', '').strip()
            job_type = request.form.get('job_type', 'Full-time').strip()
            education_req = request.form.get('education_req', '').strip()
            experience_req = request.form.get('experience_req', 'Fresher').strip()
            required_skills = request.form.get('required_skills', '').strip()
            description = request.form.get('description', '').strip()
            responsibilities = request.form.get('responsibilities', '').strip()
            eligibility_notes = request.form.get('eligibility_notes', '').strip()
            contact_email = request.form.get('contact_email', '').strip()
            is_active = 1 if request.form.get('is_active') == 'on' else 0

            models.update_job(job_id, {
                'title': title,
                'company': company,
                'location': location,
                'role_category': role_category,
                'job_type': job_type,
                'education_req': education_req,
                'experience_req': experience_req,
                'required_skills': required_skills,
                'description': description,
                'responsibilities': responsibilities,
                'eligibility_notes': eligibility_notes,
                'contact_email': contact_email,
                'is_active': is_active
            })

            flash(f'Job posting "{title}" updated successfully. Updated skill requirements reflect instantly!', 'success')
            return redirect(url_for('admin_manage_jobs'))

        return render_template('admin/job_form.html', form_data=job, is_edit=True, title=f'Edit Job: {job["title"]}')

    @app.route('/admin/jobs/delete/<int:job_id>', methods=['POST'])
    @admin_required
    def admin_delete_job(job_id):
        """Delete a job posting."""
        models.delete_job(job_id)
        flash('Job posting deleted successfully.', 'info')
        return redirect(url_for('admin_manage_jobs'))

    @app.route('/admin/jobs/toggle/<int:job_id>', methods=['POST'])
    @admin_required
    def admin_toggle_job(job_id):
        """Toggle active / inactive status of a job posting."""
        models.toggle_job_status(job_id)
        flash('Job status updated.', 'info')
        return redirect(url_for('admin_manage_jobs'))

    @app.route('/admin/students')
    @admin_required
    def admin_students():
        """View list of all registered students, their qualifications and skills."""
        students = models.get_all_students()
        return render_template('admin/students.html', students=students, title='Registered Students')

    # ---------------------------------------------------------
    # API Endpoints (For Dynamic Interactive Checks)
    # ---------------------------------------------------------
    @app.route('/api/match-preview', methods=['POST'])
    def api_match_preview():
        """Calculates match score between candidate skills and required skills on the fly."""
        data = request.get_json() or {}
        candidate_skills = data.get('candidate_skills', '')
        required_skills = data.get('required_skills', '')

        result = matching_engine.calculate_match(candidate_skills, required_skills)
        return jsonify(result)

    # ---------------------------------------------------------
    # Error Handlers
    # ---------------------------------------------------------
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', not_found=True, title='Page Not Found'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('base.html', server_error=True, title='Server Error'), 500

    return app

app = create_app()

if __name__ == '__main__':
    print("=" * 70)
    print("FRESHER JOB AND SKILL GUIDANCE PORTAL")
    print("Master of Computer Application (MCA) Mini Project")
    print("Author: Dhammadip Harshabodh Shirsath (Roll no: 47)")
    print("=" * 70)
    print("Starting Flask server at http://127.0.0.1:5000")
    print("Admin credentials:   admin@fresherportal.com / Admin@123")
    print("Student credentials: dhammadip@student.ac.in / Student@123")
    print("=" * 70)
    app.run(debug=True, host='127.0.0.1', port=5000)
