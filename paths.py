"""
Path Configuration for ModularNucleoid P2P Demo
Centralized path management using pathlib
"""

from pathlib import Path

# Base application directory
BASE_DIR = Path(__file__).parent.resolve()

# Core directories
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
LOGS_DIR = BASE_DIR / "logs"
ROUTES_DIR = BASE_DIR / "routes"
UTILS_DIR = BASE_DIR / "utils"

# Static subdirectories
CSS_DIR = STATIC_DIR / "css"
JS_DIR = STATIC_DIR / "js"
UPLOADS_DIR = STATIC_DIR / "uploads"
IMAGES_DIR = STATIC_DIR / "images"

# Database paths
DATABASE_DIR = BASE_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "database.db"
BACKUP_DIR = DATABASE_DIR / "backups"

# Configuration paths
ENV_FILE = BASE_DIR / ".env"
CONFIG_DIR = BASE_DIR / "config"

# Log file paths
APP_LOG = LOGS_DIR / "app.log"
ERROR_LOG = LOGS_DIR / "error.log"
ACCESS_LOG = LOGS_DIR / "access.log"

def ensure_directories():
    """Ensure all necessary directories exist"""
    directories = [
        LOGS_DIR,
        UPLOADS_DIR,
        IMAGES_DIR,
        DATABASE_DIR,
        BACKUP_DIR,
        CONFIG_DIR
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_upload_path(filename: str) -> Path:
    """Get safe upload path for a filename"""
    from utils.helpers import sanitize_filename
    safe_filename = sanitize_filename(filename)
    return UPLOADS_DIR / safe_filename

def get_log_path(log_type: str) -> Path:
    """Get log file path by type"""
    log_paths = {
        'app': APP_LOG,
        'error': ERROR_LOG,
        'access': ACCESS_LOG
    }
    return log_paths.get(log_type, APP_LOG)

# Initialize directories on import
ensure_directories()
