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

@main_bp.route('/fortran')
def fortran():
    """
    Renders the Fortran WebAssembly pipeline testing page.
    Provides interface for compiling Fortran code to WASM and testing execution.
    """
    try:
        # Future: Add statistics about compiled WASM modules, performance benchmarks, etc.
        return render_template('fortran.html', title='Fortran WASM Pipeline')
    except Exception as e:
        current_app.logger.error(f"Error loading Fortran WASM page: {e}")
        return render_template('fortran.html', title='Fortran WASM Pipeline',
                               error_message="Could not load Fortran WASM interface.")

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

@main_bp.route('/workers')
def workers():
    return render_template('workers.html', title='Workers')

@main_bp.route('/workers') # <-- Using main_bp.route here
def workers():
    """Renders the workers page with the list of workers and the add form."""
    return render_template('workers.html', workers=workers_data)

@main_bp.route('/add_worker', methods=['POST']) # <-- Using main_bp.route here
def add_worker():
    """Handles the form submission for adding a new worker."""
    global next_worker_id # To modify the global ID counter

    if request.method == 'POST':
        worker_name = request.form.get('worker_name')
        ip_address = request.form.get('ip_address')
        ssh_username = request.form.get('ssh_username')
        ssh_private_key_path = request.form.get('ssh_private_key_path')
        ssh_passphrase = request.form.get('ssh_passphrase')

        if not all([worker_name, ip_address, ssh_username, ssh_private_key_path]):
            flash('All required fields must be filled out!', 'danger')
            # Redirect using the blueprint name: 'blueprint_name.route_function_name'
            return redirect(url_for('main.workers'))

        # In a real application, you would:
        # 1. Validate inputs more thoroughly (e.g., IP address format, path existence).
        # 2. Store this data in a database.
        # 3. Potentially initiate a background task to check SSH connection/provision.

        new_worker = {
            'id': next_worker_id,
            'name': worker_name,
            'ip_address': ip_address,
            'ssh_username': ssh_username,
            'ssh_private_key_path': ssh_private_key_path,
            'ssh_passphrase': ssh_passphrase if ssh_passphrase else 'N/A', # Store securely in real app
            'status': 'provisioning', # Initial status
            'last_check': 'N/A'
        }
        workers_data.append(new_worker)
        next_worker_id += 1

        flash(f'Worker "{worker_name}" added successfully!', 'success')
        return redirect(url_for('main.workers'))

    # If somehow a GET request hits this route, redirect or error
    return redirect(url_for('main.workers'))


@main_bp.route('/manage_worker/<int:worker_id>') # <-- Using main_bp.route here
def manage_worker(worker_id):
    # Logic to fetch and display details for a specific worker
    worker = next((w for w in workers_data if w['id'] == worker_id), None)
    if worker:
        return f"Managing worker: {worker['name']} ({worker['id']})" # Placeholder
    flash('Worker not found.', 'danger')
    return redirect(url_for('main.workers'))


@main_bp.route('/remove_worker/<int:worker_id>', methods=['POST']) # <-- Using main_bp.route here
def remove_worker(worker_id):
    global workers_data
    # In a real app, you'd remove from DB
    original_len = len(workers_data)
    workers_data = [w for w in workers_data if w['id'] != worker_id]
    if len(workers_data) < original_len:
        flash(f'Worker removed successfully.', 'success')
    else:
        flash(f'Worker not found.', 'danger')
    return redirect(url_for('main.workers'))



# You can add more routes here for specific compound details, etc.
# @main_bp.route('/compound/<int:compound_id>')
# def compound_detail(compound_id):
#     db = current_app.extensions['sqlalchemy']
#     compound = db.session.query(Compound).get_or_404(compound_id)
#     return render_template('compound_detail.html', title=compound.name, compound=compound)