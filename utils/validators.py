"""
Validation utility functions
"""

import re
from pathlib import Path

def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_filename(filename: str) -> bool:
    """
    Validate filename for basic safety.
    Checks for characters typically disallowed or problematic in filenames.
    """
    # Disallow path traversal, null bytes, and common forbidden characters
    if ".." in filename or "/" in filename or "\\" in filename or "\\0" in filename:
        return False
    # Basic check for empty or excessively long names (though sanitize_filename handles length)
    if not filename or len(filename) > 255:
        return False
    # Regex to allow alphanumeric, periods, hyphens, underscores
    pattern = r"^[a-zA-Z0-9_.-]+$"
    return re.match(pattern, filename) is not None

# Add more validation functions as needed, e.g., for passwords, user inputs etc.
