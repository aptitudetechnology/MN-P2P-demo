
import sqlite3
import logging
from pathlib import Path
from paths import DATABASE_PATH, DATABASE_DIR

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get SQLite database connection with row factory"""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True) # Ensure database directory exists
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database with all required tables"""
    conn = get_db_connection()

    try:
        # App settings table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Activity log table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                user_ip TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # User authentication table
        conn.execute('''    CREATE TABLE IF NOT EXISTS users (        id INTEGER PRIMARY KEY AUTOINCREMENT,        username TEXT UNIQUE NOT NULL,        email TEXT UNIQUE NOT NULL,        password_hash TEXT NOT NULL,        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,        last_login TIMESTAMP,        is_active BOOLEAN DEFAULT 1,        is_admin BOOLEAN DEFAULT 0    )''')

        # Insert default settings
        default_settings = [
            ('app_name', 'ModularNucleoid P2P Demo', 'Application name'),
            ('version', '1.0.0', 'Application version'),
            ('maintenance_mode', 'false', 'Maintenance mode status')
        ]

        for key, value, description in default_settings:
            conn.execute('''
                INSERT OR IGNORE INTO app_settings (key, value, description)
                VALUES (?, ?, ?)
            ''', (key, value, description))

        conn.commit()
        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_setting(key: str, default=None):
    """Get application setting by key"""
    conn = get_db_connection()
    try:
        cursor = conn.execute('SELECT value FROM app_settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        return result['value'] if result else default
    finally:
        conn.close()

def set_setting(key: str, value: str, description: str = None):
    """Set application setting"""
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT OR REPLACE INTO app_settings (key, value, description, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (key, value, description))
        conn.commit()
        logger.info(f"Setting updated: {key} = {value}")
    finally:
        conn.close()

def log_activity(action: str, user_ip: str = None, details: str = None):
    """Log user activity to the database"""
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO activity_log (action, user_ip, details)
            VALUES (?, ?, ?)
        ''', (action, user_ip, details))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")
    finally:
        conn.close()
