from flask import Blueprint, render_template, current_app, request, jsonify
# Import models and db here if your views need to interact with the database
from models.models import Compound, BiochemicalGroup, TherapeuticArea, Disease, Study
from app import db # Assuming 'db' is globally accessible from app.py as per previous fixes

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """
    Renders the main dashboard page.
    Fetches some summary data for display.
    """
    try:
        total_compounds = Compound.query.count()
        # Example: get recent compounds for a dashboard overview
        recent_compounds = Compound.query.order_by(Compound.created_at.desc()).limit(5).all()
        return render_template('dashboard.html', title='Dashboard',
                               total_compounds=total_compounds,
                               recent_compounds=recent_compounds)
    except Exception as e:
        current_app.logger.error(f"Error loading dashboard data: {e}")
        # Render the dashboard even if data loading fails, showing an error message
        return render_template('dashboard.html', title='Dashboard',
                               error_message="Could not load dashboard data. Database might be empty or inaccessible.")

@main_bp.route('/compounds')
def compounds():
    """
    Renders the compounds listing page.
    Fetches all compounds to display in a list.
    """
    try:
        all_compounds = Compound.query.all()
        return render_template('compounds.html', title='Compounds', compounds=all_compounds)
    except Exception as e:
        current_app.logger.error(f"Error loading compounds data: {e}")
        return render_template('compounds.html', title='Compounds',
                               error_message="Could not load compounds data. Database might be empty or inaccessible.")

@main_bp.route('/p2p-demo')
def p2p_demo():
    """Renders the P2P demo page."""
    return render_template('p2p_demo.html', title='P2P Demo')

@main_bp.route('/settings')
def settings():
    """Renders the settings page."""
    return render_template('settings.html', title='Settings')

# You can add more routes here for specific compound details, etc.
# @main_bp.route('/compound/<int:compound_id>')
# def compound_detail(compound_id):
#     compound = Compound.query.get_or_404(compound_id)
#     return render_template('compound_detail.html', title=compound.name, compound=compound)

