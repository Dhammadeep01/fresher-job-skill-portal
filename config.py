import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fresher-portal-mca-mini-project-secret-key-2026')
    DATABASE = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'fresher_portal.db'))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
