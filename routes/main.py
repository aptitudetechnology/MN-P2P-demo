"""
Main application routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from utils.database import get_db_connection
from utils.helpers import log_user_action
import logging

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """Main dashboard"""
    log_user_action('dashboard_visit', request.remote_addr)
    return render_template('dashboard.html', title='Dashboard')



@main_bp.route('/settings')
def settings():
    """Application settings"""
    return render_template('settings.html', title='Settings')

# Example: A simple form route
@main_bp.route('/submit_feedback', methods=['GET', 'POST'])
def submit_feedback():
    if request.method == 'POST':
        feedback_text = request.form.get('feedback_text')
        if feedback_text:
            # In a real app, you'd save this to a database
            logger.info(f"Received feedback: {feedback_text} from {request.remote_addr}")
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Feedback cannot be empty.', 'error')
    return render_template('feedback.html', title='Submit Feedback')
