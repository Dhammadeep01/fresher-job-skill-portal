/**
 * Fresher Job & Skill Guidance Portal
 * Interactive Frontend JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Alert Dismissal
    const alertCloses = document.querySelectorAll('.alert-close');
    alertCloses.forEach(btn => {
        btn.addEventListener('click', function () {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-6px)';
                setTimeout(() => alert.remove(), 250);
            }
        });
    });

    // 2. Demo Login Helpers
    const fillAdminBtn = document.getElementById('btn-fill-admin');
    const fillStudentBtn = document.getElementById('btn-fill-student');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    if (fillAdminBtn && emailInput && passwordInput) {
        fillAdminBtn.addEventListener('click', function (e) {
            e.preventDefault();
            emailInput.value = 'admin@fresherportal.com';
            passwordInput.value = 'Admin@123';
        });
    }

    if (fillStudentBtn && emailInput && passwordInput) {
        fillStudentBtn.addEventListener('click', function (e) {
            e.preventDefault();
            emailInput.value = 'dhammadip@student.ac.in';
            passwordInput.value = 'Student@123';
        });
    }

    // 3. Interactive Tag Input Component
    initSkillTagsInput();
});

/**
 * Initializes interactive skill tag input containers
 */
function initSkillTagsInput() {
    const skillInput = document.getElementById('skills-input');
    const tagsContainer = document.getElementById('skill-tags-display');
    const addBtn = document.getElementById('btn-add-skill');
    const quickPills = document.querySelectorAll('.quick-skill-pill');

    if (!skillInput || !tagsContainer) return;

    function renderTags() {
        tagsContainer.innerHTML = '';
        const raw = skillInput.value || '';
        const skills = raw.split(',').map(s => s.trim()).filter(s => s.length > 0);

        skills.forEach((skill, index) => {
            const tag = document.createElement('span');
            tag.className = 'badge badge-primary';
            tag.style.fontSize = '0.82rem';
            tag.style.padding = '0.35rem 0.65rem';
            tag.innerHTML = `
                <span>${escapeHtml(skill)}</span>
                <button type="button" class="btn-remove-tag" data-index="${index}" style="background:none;border:none;color:inherit;cursor:pointer;margin-left:4px;font-weight:bold;">&times;</button>
            `;
            tagsContainer.appendChild(tag);
        });

        // Attach removal listeners
        tagsContainer.querySelectorAll('.btn-remove-tag').forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const idx = parseInt(this.getAttribute('data-index'), 10);
                const currentSkills = (skillInput.value || '').split(',').map(s => s.trim()).filter(s => s.length > 0);
                currentSkills.splice(idx, 1);
                skillInput.value = currentSkills.join(', ');
                renderTags();
            });
        });
    }

    function addSkill(newSkill) {
        const trimmed = (newSkill || '').trim();
        if (!trimmed) return;

        const currentSkills = (skillInput.value || '').split(',').map(s => s.trim()).filter(s => s.length > 0);
        // Case insensitive duplicate check
        const exists = currentSkills.some(s => s.toLowerCase() === trimmed.toLowerCase());
        if (!exists) {
            currentSkills.push(trimmed);
            skillInput.value = currentSkills.join(', ');
            renderTags();
        }
    }

    // Quick add pill clicks
    quickPills.forEach(pill => {
        pill.addEventListener('click', function (e) {
            e.preventDefault();
            const skillToAdd = this.getAttribute('data-skill') || this.innerText;
            addSkill(skillToAdd);
        });
    });

    // Custom skill add button
    const customSkillField = document.getElementById('custom-skill-name');
    if (addBtn && customSkillField) {
        addBtn.addEventListener('click', function (e) {
            e.preventDefault();
            addSkill(customSkillField.value);
            customSkillField.value = '';
            customSkillField.focus();
        });

        customSkillField.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addSkill(this.value);
                this.value = '';
            }
        });
    }

    // Initial render
    renderTags();
    
    // Listen for manual edits in the input
    skillInput.addEventListener('input', renderTags);
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.innerText = str;
    return div.innerHTML;
}
