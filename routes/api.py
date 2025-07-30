"""
API routes for REST endpoints
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
from utils.database import get_db_connection, get_setting # get_setting for potential API key validation
from utils.helpers import validate_api_key # Assuming you'd add this utility
import logging

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)

@api_bp.route('/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": get_setting('version', 'N/A'),
        "service": "ModularNucleoid P2P Demo"
    })

@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()

        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"API Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@api_bp.route('/data')
def get_data():
    """Get application data (example protected endpoint)"""
    # Example API endpoint - customize as needed
    # if not validate_api_key(request.headers.get('X-API-Key')):
    #     return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_db_connection()
        # Fetch some example data; adjust query as per your app's needs
        cursor = conn.execute('SELECT key, value FROM app_settings LIMIT 10')
        data = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify({
            "success": True,
            "data": data,
            "count": len(data)
        })
    except Exception as e:
        logger.error(f"API data fetch failed: {e}")
        return jsonify({
            "success": False,
            "error": "Data fetch failed"
        }), 500
