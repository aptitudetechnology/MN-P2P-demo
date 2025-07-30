"""
ModularNucleoid P2P Demo
A Flask web application: ModularNucleoid P2P Demo (Fortran + Wasm + PeerJS)

Author: SMILHS
Generated: 2025-07-30 11:44:47
"""

import os
import logging
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime

# Import blueprints from the routes package
from routes import register_blueprints

# Import utilities
from utils.database import init_db, get_db_connection, get_setting
from utils.helpers import format_datetime
import json

# Path configuration
from paths import BASE_DIR, LOGS_DIR



# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
app.config['APPLICATION_NAME'] = 'ModularNucleoid P2P Demo'
app.config['DATABASE_PATH'] = BASE_DIR / 'data' / 'database.db'



# Initialize extensions


# Logging setup
LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Register Blueprints
register_blueprints(app)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 Not Found: {request.path}")
    return render_template('error.html', error="Page not found", code=404), 404

@app.errorhandler(500)
def server_error(error):
    logger.exception(f"500 Internal Server Error: {error}")
    return render_template('error.html', error="Internal server error", code=500), 500

# Template context processors
@app.context_processor
def inject_globals():
    """Inject global variables and functions into all templates"""
    nav_items_data =     [
        {
            "name": "Dashboard",
            "route": "/",
            "icon": "home"
        },
        {
        "name": "P2P Demo",
        "route": "/p2p-demo",
        "icon": "diagram-2"
        },
        {
            "name": "Settings",
            "route": "/settings",
            "icon": "gear"
        }
    ]
    return dict(
        nav_items=nav_items_data,
        app_title=app.config['APPLICATION_NAME'],
        current_year=datetime.now().year,
        get_setting=get_setting,
        format_datetime=format_datetime
    )

if __name__ == '__main__':
    with app.app_context():
        init_db()
        

    debug = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))

    logger.info(f"Starting {app.config.get('APPLICATION_NAME', 'ModularNucleoid P2P Demo')} on http://0.0.0.0:{port}")
    app.run(debug=debug, port=port, host='0.0.0.0')
