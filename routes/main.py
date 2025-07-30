import logging
from flask import Blueprint, render_template, request, flash, redirect, url_for
# Corrected: Changed to absolute import for models
from models import Compound, BiochemicalGroup, TherapeuticArea, Disease, Study, db
from sqlalchemy import func

main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main_bp.route('/')
def dashboard():
    """Renders the dashboard page."""
    # Example data for dashboard, replace with actual data fetching if needed
    total_compounds = Compound.query.count()
    total_biochemical_groups = BiochemicalGroup.query.count()
    total_therapeutic_areas = TherapeuticArea.query.count()
    
    # You might want to fetch more specific data for the dashboard here
    
    return render_template('dashboard.html', 
                           title='Dashboard',
                           total_compounds=total_compounds,
                           total_biochemical_groups=total_biochemical_groups,
                           total_therapeutic_areas=total_therapeutic_areas)

@main_bp.route('/compounds')
def compounds():
    """Renders the compounds listing page with search and filters."""
    try:
        # Fetch all compounds (or apply search/filter logic later)
        all_compounds = Compound.query.all()

        # --- Calculate statistics for the compounds page ---
        # Total counts
        total_compounds = Compound.query.count()
        biochemical_groups_count = BiochemicalGroup.query.count()
        therapeutic_areas_count = TherapeuticArea.query.count()

        # Compounds by Clinical Phase
        phase_stats_query = db.session.query(
            Compound.clinical_phase,
            func.count(Compound.id)
        ).group_by(Compound.clinical_phase).all()
        # Convert to a dictionary for easier access in template
        phase_stats = {phase or "Unknown": count for phase, count in phase_stats_query}

        # Compounds by Biochemical Group
        group_stats_query = db.session.query(
            BiochemicalGroup.name,
            func.count(Compound.id)
        ).outerjoin(Compound, BiochemicalGroup.id == Compound.biochemical_group_id).group_by(BiochemicalGroup.name).all()
        # Convert to a dictionary
        group_stats = {group: count for group, count in group_stats_query}

        # Aggregate all stats into a single dictionary
        stats = {
            'total_compounds': total_compounds,
            'biochemical_groups_count': biochemical_groups_count, # Renamed for clarity
            'therapeutic_areas_count': therapeutic_areas_count,   # Renamed for clarity
            'phase_stats': phase_stats,
            'group_stats': group_stats
        }
        # --- End statistics calculation ---

        return render_template('compounds.html', 
                               title='Compounds',
                               compounds=all_compounds,
                               stats=stats) # Pass the calculated stats to the template
    except Exception as e:
        logger.error(f"Error loading compounds data: {e}")
        flash('Error loading compounds data. Please try again later.', 'danger')
        return redirect(url_for('main.dashboard')) # Redirect to dashboard or an error page

@main_bp.route('/compound/<int:compound_id>')
def compound_detail(compound_id):
    """Renders the detail page for a specific compound."""
    compound = Compound.query.get_or_404(compound_id)
    return render_template('compound_detail.html', title=compound.name, compound=compound)

@main_bp.route('/p2p-demo')
def p2p_demo():
    """Renders the P2P demo page."""
    return render_template('p2p_demo.html', title='P2P Demo')

@main_bp.route('/simulate') # NEW: Placeholder route for /simulate
def simulate():
    """Renders a placeholder page for simulation."""
    return render_template('simulate.html', title='Simulation')

@main_bp.route('/settings')
def settings():
    """Renders the settings page."""
    return render_template('settings.html', title='Settings')

# Add other routes as needed
