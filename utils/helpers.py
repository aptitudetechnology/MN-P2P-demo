"""
General helper functions
"""

import re
import logging
from datetime import datetime
from pathlib import Path
from utils.database import log_activity # Correct import path

logger = logging.getLogger(__name__)

def log_user_action(action: str, user_ip: str = None, details: str = None):
    """Log user action to database"""
    try:
        log_activity(action, user_ip, details)
    except Exception as e:
        logger.error(f"Failed to log user action: {{e}}")

def format_datetime(dt, format_str="%Y-%m-%d %H:%M:%S"):
    """Format datetime object or string to string"""
    if isinstance(dt, str):
        try:
            # Attempt to parse string to datetime object first, then format
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00')) # Handle 'Z' for UTC
        except ValueError:
            pass # Keep as string if parsing fails, or handle error
    if not isinstance(dt, datetime):
        # If it's still not a datetime object (e.g., failed parsing or None), return empty string
        return ""
    return dt.strftime(format_str)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    # Limit length (e.g., to 255 characters for many file systems)
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_len = 255 - (len(ext) + 1 if ext else 0)
        filename = name[:max_name_len] + ('.' + ext if ext else '')
    return filename

def get_file_size_human(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f}{size_names[i]}"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def generate_unique_filename(original_filename: str, upload_dir: Path) -> str:
    """Generate unique filename to avoid conflicts"""
    base_name = sanitize_filename(original_filename)
    name, ext = base_name.rsplit('.', 1) if '.' in base_name else (base_name, '')

    counter = 1
    unique_name = base_name

    while (upload_dir / unique_name).exists():
        unique_name = f"{name}_{counter}" + (f".{ext}" if ext else "")
        counter += 1

    return unique_name

# Example for API Key validation - needs implementation
def validate_api_key(api_key: str) -> bool:
    """
    Validate an API key.
    In a real application, this would check against a database of valid API keys.
    """
    # For demonstration, a hardcoded key. Replace with proper lookup.
    VALID_API_KEY = "your_super_secret_api_key_123"
    return api_key == VALID_API_KEY
