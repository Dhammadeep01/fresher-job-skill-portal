import re

# Synonym mapping to assist matching natural variations in skill names
SKILL_SYNONYMS = {
    'js': 'javascript',
    'javascript': 'javascript',
    'py': 'python',
    'python': 'python',
    'html': 'html5',
    'html5': 'html5',
    'css': 'css3',
    'css3': 'css3',
    'react': 'react',
    'reactjs': 'react',
    'react.js': 'react',
    'node': 'nodejs',
    'nodejs': 'nodejs',
    'node.js': 'nodejs',
    'express': 'expressjs',
    'expressjs': 'expressjs',
    'postgres': 'postgresql',
    'postgresql': 'postgresql',
    'mongo': 'mongodb',
    'mongodb': 'mongodb',
    'spring': 'spring boot',
    'springboot': 'spring boot',
    'spring boot': 'spring boot',
    'c++': 'cpp',
    'c#': 'csharp',
    'rest': 'rest apis',
    'restful': 'rest apis',
    'rest api': 'rest apis',
    'rest apis': 'rest apis',
    'apis': 'rest apis',
    'power bi': 'powerbi',
    'powerbi': 'powerbi',
    'aws': 'aws',
    'amazon web services': 'aws',
}

def normalize_skill(skill: str) -> str:
    """Normalize a skill name for robust comparison."""
    if not skill:
        return ""
    # Lowercase and strip whitespace
    cleaned = skill.strip().lower()
    # Normalize common symbols like 'c++' -> 'cpp', 'c#' -> 'csharp'
    if cleaned in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[cleaned]
    # Remove excessive punctuation
    simplified = re.sub(r'[\._\-]', '', cleaned)
    if simplified in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[simplified]
    return cleaned

def parse_skills(skills_input) -> list:
    """
    Parse skills from either a comma/newline separated string or an iterable list.
    Returns a clean list of non-empty, stripped skill strings in their display form.
    """
    if not skills_input:
        return []
    if isinstance(skills_input, list):
        items = skills_input
    else:
        # Split by comma, semicolon, or newline
        items = re.split(r'[,;\n]+', str(skills_input))
    
    unique_skills = []
    seen = set()
    for item in items:
        cleaned = item.strip()
        if cleaned:
            norm = normalize_skill(cleaned)
            if norm not in seen:
                seen.add(norm)
                unique_skills.append(cleaned)
    return unique_skills

def calculate_match(candidate_skills, required_skills) -> dict:
    """
    Deterministic rule-based job matching calculation:
    Match Score (%) = (Matched Skills / Required Skills) * 100
    
    Returns:
        dict: {
            'match_score': int (0-100),
            'matched_skills': list of matched required skill names,
            'missing_skills': list of missing required skill names,
            'extra_skills': candidate skills not required for this role,
            'total_required': int,
            'matched_count': int,
            'match_level': str ('Strong Match', 'Moderate Match', 'Low Match'),
            'badge_class': str ('success', 'warning', 'danger'),
            'summary_text': str
        }
    """
    candidate_list = parse_skills(candidate_skills)
    required_list = parse_skills(required_skills)
    
    # Map normalized representations back to display forms
    cand_norm_map = {normalize_skill(s): s for s in candidate_list}
    req_norm_map = {normalize_skill(s): s for s in required_list}
    
    cand_norm_set = set(cand_norm_map.keys())
    req_norm_set = set(req_norm_map.keys())
    
    total_required = len(req_norm_set)
    
    if total_required == 0:
        # If no specific skills required, default to 100% suitability
        return {
            'match_score': 100,
            'matched_skills': [],
            'missing_skills': [],
            'extra_skills': candidate_list,
            'total_required': 0,
            'matched_count': 0,
            'match_level': 'General Fit',
            'badge_class': 'success',
            'summary_text': 'No specific prerequisite skills enforced for this fresher position.'
        }
    
    matched_norm = req_norm_set.intersection(cand_norm_set)
    missing_norm = req_norm_set.difference(cand_norm_set)
    extra_norm = cand_norm_set.difference(req_norm_set)
    
    matched_skills = [req_norm_map[k] for k in req_norm_set if k in matched_norm]
    missing_skills = [req_norm_map[k] for k in req_norm_set if k in missing_norm]
    extra_skills = [cand_norm_map[k] for k in cand_norm_set if k in extra_norm]
    
    matched_count = len(matched_norm)
    # Match Score Formula: (Matched Skills / Required Skills) * 100
    score_percentage = round((matched_count / total_required) * 100)
    
    # Determine suitability tier
    if score_percentage >= 80:
        match_level = 'Strong Match'
        badge_class = 'success'
    elif score_percentage >= 50:
        match_level = 'Moderate Match'
        badge_class = 'warning'
    else:
        match_level = 'Low Match'
        badge_class = 'danger'
        
    summary_text = f"You match {matched_count} of {total_required} required skills ({score_percentage}%)."
    
    return {
        'match_score': score_percentage,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'extra_skills': extra_skills,
        'total_required': total_required,
        'matched_count': matched_count,
        'match_level': match_level,
        'badge_class': badge_class,
        'summary_text': summary_text
    }

def get_skill_guidance(missing_skills, conn=None) -> list:
    """
    Retrieve structured skill guidance and learning paths for missing skills.
    Queries the knowledge base table or synthesizes actionable advice.
    """
    if not missing_skills:
        return []
        
    guidance_results = []
    
    # Check if database connection available
    kb_data = {}
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM skill_guidance")
            rows = cursor.fetchall()
            for row in rows:
                norm_name = normalize_skill(row['skill_name'])
                kb_data[norm_name] = dict(row)
        except Exception:
            pass
            
    for skill in missing_skills:
        norm = normalize_skill(skill)
        if norm in kb_data:
            item = kb_data[norm]
            guidance_results.append({
                'skill_name': skill,
                'category': item.get('category', 'Technical Skill'),
                'description': item.get('description', f'Essential industry skill for modern development roles.'),
                'why_it_matters': item.get('why_it_matters', f'Required to successfully execute core responsibilities in this job role.'),
                'resources': [r.strip() for r in item.get('recommended_resources', '').split('\n') if r.strip()],
                'mini_project': item.get('mini_project_idea', f'Build a mini project demonstrating practical application of {skill}.'),
                'estimated_time': item.get('estimated_time', '1-2 weeks')
            })
        else:
            # Fallback dynamic guidance
            guidance_results.append({
                'skill_name': skill,
                'category': 'Role Competency',
                'description': f'{skill} is a targeted requirement identified in this fresher job listing.',
                'why_it_matters': f'Recruiters look for foundational knowledge of {skill} to reduce team onboarding and ramp-up time.',
                'resources': [
                    f'• Official documentation and developer tutorials for {skill}',
                    f'• freeCodeCamp / Coursera introductory modules on {skill}',
                    f'• YouTube crash courses and hands-on coding walkthroughs'
                ],
                'mini_project': f'Create a mini demo project showcasing your grasp of {skill} and publish the code to your GitHub profile.',
                'estimated_time': '1-2 weeks of focused practice'
            })
            
    return guidance_results

def rank_jobs_for_student(candidate_skills, jobs, conn=None) -> list:
    """
    Takes student skills and a list of job dicts/rows.
    Computes rule-based match scores, missing skills, and guidance for each job.
    Returns the list sorted descending by match score.
    """
    scored_jobs = []
    for job in jobs:
        job_dict = dict(job)
        req_skills_str = job_dict.get('required_skills', '')
        match_info = calculate_match(candidate_skills, req_skills_str)
        
        job_dict.update(match_info)
        # Attach guidance for missing skills
        job_dict['missing_guidance'] = get_skill_guidance(match_info['missing_skills'], conn)
        scored_jobs.append(job_dict)
        
    # Sort primarily by match score descending, then by job ID descending
    scored_jobs.sort(key=lambda x: (x['match_score'], x.get('id', 0)), reverse=True)
    return scored_jobs
