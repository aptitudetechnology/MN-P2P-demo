from flask import Blueprint, render_template, current_app, request, jsonify
from sqlalchemy import func
from datetime import datetime, timedelta # Ensure datetime and timedelta are imported

# Import models directly. They already get 'db' from 'app' via 'from app import db' in models.py
from models.models import Compound, BiochemicalGroup, TherapeuticArea, Disease, Study


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """
    Renders the main dashboard page.
    Fetches comprehensive data for display, including P2P/DNA context and stats.
    """
    # Access the db instance from the current application context
    db = current_app.extensions['sqlalchemy']
    try:
        # Data for Quick Stats and Recent Compounds sections
        total_compounds = db.session.query(Compound).count()
        recent_compounds = db.session.query(Compound).order_by(Compound.created_at.desc()).limit(5).all()

        # Pass datetime.utcnow() for server time display
        server_datetime = datetime.utcnow()

        return render_template('dashboard.html', title='Dashboard',
                               total_compounds=total_compounds,
                               recent_compounds=recent_compounds,
                               datetime=server_datetime) # Pass datetime for server time display
    except Exception as e:
        current_app.logger.error(f"Error loading dashboard data: {e}")
        # Render the dashboard even if data loading fails, showing an error message
        return render_template('dashboard.html', title='Dashboard',
                               error_message="Could not load dashboard data. Database might be empty or inaccessible.")

@main_bp.route('/compounds')
def compounds():
    """
    Renders the compounds listing page.
    Fetches all compounds and relevant statistics to display.
    """
    # Access the db instance from the current application context
    db = current_app.extensions['sqlalchemy']
    try:
        all_compounds = db.session.query(Compound).all()
        
        # Calculate statistics needed by the template
        total_compounds = db.session.query(Compound).count()
        biochemical_groups_count = db.session.query(BiochemicalGroup).count()
        therapeutic_areas_count = db.session.query(TherapeuticArea).count()

        # Calculate recent additions (e.g., compounds added in the last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_additions_count = db.session.query(Compound).filter(Compound.created_at >= thirty_days_ago).count()

        # Create a stats dictionary to pass to the template
        stats = {
            'total_compounds': total_compounds,
            'biochemical_groups': biochemical_groups_count,
            'therapeutic_areas': therapeutic_areas_count,
            'recent_additions': recent_additions_count,
        }

        # Fetch data for filters and periodic table navigation (if needed on compounds page)
        biochemical_groups_data = db.session.query(BiochemicalGroup).all()
        diseases_data = db.session.query(Disease).all()

        return render_template('compounds.html', title='Compounds',
                               compounds=all_compounds,
                               stats=stats, # Pass the 'stats' dictionary
                               biochemical_groups=biochemical_groups_data, # Pass groups for filters
                               diseases=diseases_data) # Pass diseases for filters
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

@main_bp.route('/simulate')
def simulate():
    """Renders the simulation page."""
    return render_template('simulate.html', title='Simulation')

# You can add more routes here for specific compound details, etc.
# @main_bp.route('/compound/<int:compound_id>')
# def compound_detail(compound_id):
#     db = current_app.extensions['sqlalchemy']
#     compound = db.session.query(Compound).get_or_404(compound_id)
#     return render_template('compound_detail.html', title=compound.name, compound=compound)
