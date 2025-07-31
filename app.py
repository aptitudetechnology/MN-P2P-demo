"""
ModularNucleoid P2P Demo
A Flask web application: ModularNucleoid P2P Demo (Fortran + Wasm + PeerJS)
Author: SMILHS
Generated: 2025-07-30 11:44:47
Updated: 2025-07-31 - Added SQLAlchemy integration and Application Factory (Circular Import Fix)
"""
import os
import logging
import click
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from datetime import datetime
import json

# Path configuration
from paths import BASE_DIR, LOGS_DIR

from flask_wtf.csrf import CSRFProtect

# Logging setup - moved outside create_app for global access
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

def create_app():
    """
    Application factory function to create and configure the Flask app.
    This helps avoid circular imports and ensures extensions are initialized correctly.
    """
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    csrf = CSRFProtect(app)
    # Enable CORS for all route
    # Configuration
    app.config['APPLICATION_NAME'] = 'ModularNucleoid P2P Demo'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{BASE_DIR / "data" / "compounds.db"}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CACHE_TYPE'] = 'simple'

    # Ensure data directory exists
    (BASE_DIR / 'data').mkdir(parents=True, exist_ok=True)

    # IMPORTANT: Import db from models *inside* create_app, after the app instance is created.
    # This breaks the circular import dependency.
    #from models import db
    from extensions import db
 
    
    # Initialize extensions with the app instance
    db.init_app(app) # Initialize db with the Flask app instance
    
    migrate = Migrate(app, db)
    CORS(app)
    cache = Cache(app)
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )

    # Import blueprints from the routes package. This must happen AFTER db.init_app(app)
    # to ensure models are properly loaded and db is bound.
    from routes import register_blueprints
    register_blueprints(app)

    # Import utilities (keep the helpers, but we'll use SQLAlchemy for database)
    from utils.helpers import format_datetime

    # Template context processors
    @app.context_processor
    def inject_globals():
        """Inject global variables and functions into all templates"""
        nav_items_data = [
            {
                "name": "Dashboard",
                "route": "/",
                "icon": "home"
            },
            {
                "name": "Compounds",
                "route": "/compounds",
                "icon": "flask"
            },
            {
                "name": "Fortran WASM",
                "route": "/fortran",
                "icon": "code-slash"
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
            format_datetime=format_datetime
        )

    # Helper function for backwards compatibility
    def get_setting(key, default=None):
        """Get application setting - placeholder for backwards compatibility"""
        settings = {
            'app_name': app.config['APPLICATION_NAME'],
            'version': '1.0.0'
        }
        return settings.get(key, default)

    # Add to template context for backwards compatibility
    app.jinja_env.globals['get_setting'] = get_setting

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 Not Found: {request.path}")
        return render_template('error.html', error="Page not found", code=404), 404

    @app.errorhandler(500)
    def server_error(error):
        logger.exception(f"500 Internal Server Error: {error}")
        return render_template('error.html', error="Internal server error", code=500), 500

    return app

# --- CLI Commands (defined globally, but operate on an app context) ---
# We need to create a temporary app instance for CLI commands to attach to.
# This is a common pattern for Flask CLI with app factories.
# The actual app instance for running the server will be created in __main__.

# Define CLI commands outside create_app, but use app_context to bind db
# when they are executed.
@click.group() # Make 'app' a Click group to attach commands
def cli():
    """A collection of CLI commands for the ModularNucleoid P2P Demo."""
    pass

@cli.command('init-db')
def init_db_command():
    """Initialize the database."""
    click.echo('Initializing database...')
    app_instance = create_app() # Create an app instance for the CLI command
    with app_instance.app_context():
        from models import db, Compound, BiochemicalGroup, TherapeuticArea, Disease, Study # Import models here
        db.create_all()
    click.echo('Database initialized!')

@cli.command('seed-db')
def seed_db_command():
    """Seed the database with initial data."""
    click.echo('Seeding database...')
    app_instance = create_app()
    with app_instance.app_context():
        from models import db, Compound, BiochemicalGroup, TherapeuticArea, Disease, Study # Import models here
        # Create biochemical groups
        groups_data = [
            {'name': 'Proteins', 'category': 'macromolecules', 'color': '#FF6B6B', 'description': 'Large biomolecules consisting of amino acid chains'},
            {'name': 'Nucleotides', 'category': 'building_blocks', 'color': '#4ECDC4', 'description': 'Building blocks of DNA and RNA'},
            {'name': 'Lipids', 'category': 'macromolecules', 'color': '#45B7D1', 'description': 'Fats, oils, and membrane components'},
            {'name': 'Carbohydrates', 'category': 'energy', 'color': '#96CEB4', 'description': 'Sugars and starches, primary energy sources'},
            {'name': 'Amino Acids', 'category': 'building_blocks', 'color': '#FFEAA7', 'description': 'Building blocks of proteins'},
            {'name': 'Vitamins', 'category': 'cofactors', 'color': '#DDA0DD', 'description': 'Essential organic compounds for metabolism'},
            {'name': 'Minerals', 'category': 'cofactors', 'color': '#98D8C8', 'description': 'Inorganic substances required for biological functions'},
            {'name': 'Enzymes', 'category': 'catalysts', 'color': '#F7DC6F', 'description': 'Proteins that catalyze biochemical reactions'},
            {'name': 'Hormones', 'category': 'signaling', 'color': '#BB8FCE', 'description': 'Chemical messengers in biological systems'},
            {'name': 'Neurotransmitters', 'category': 'signaling', 'color': '#85C1E9', 'description': 'Chemical messengers in the nervous system'},
            {'name': 'Alkaloids', 'category': 'secondary_metabolites', 'color': '#F8C471', 'description': 'Nitrogen-containing plant compounds'},
            {'name': 'Organic Acids', 'category': 'metabolites', 'color': '#AED6F1', 'description': 'Carboxylic acids in biological systems'},
            {'name': 'Beta-lactams', 'category': 'antibiotics', 'color': '#A9DFBF', 'description': 'Ring-structured antibiotic compounds'}
        ]
        
        for group_data in groups_data:
            group = BiochemicalGroup.query.filter_by(name=group_data['name']).first()
            if not group:
                group = BiochemicalGroup(**group_data)
                db.session.add(group)
        
        # Create therapeutic areas
        therapeutic_areas = [
            'Oncology', 'Cardiology', 'Neurology', 'Immunology', 
            'Infectious Diseases', 'Metabolic Disorders', 'Rare Diseases',
            'Pain Management', 'Endocrinology'
        ]
        
        for area_name in therapeutic_areas:
            area = TherapeuticArea.query.filter_by(name=area_name).first()
            if not area:
                area = TherapeuticArea(name=area_name)
                db.session.add(area)
        
        # Commit the reference data first
        db.session.commit()
        
        # Sample compounds with relationships
        sample_compounds_data = [
            {
                'name': 'Aspirin',
                'molecular_formula': 'C9H8O4',
                'molecular_weight': 180.16,
                'cas_number': '50-78-2',
                'smiles': 'CC(=O)OC1=CC=CC=C1C(=O)O',
                'description': 'Common pain reliever and anti-inflammatory drug',
                'clinical_phase': 'Approved',
                'mechanism_of_action': 'COX enzyme inhibitor',
                'therapeutic_areas': ['Cardiology', 'Pain Management'],
                'biochemical_group': 'Organic Acids'
            },
            {
                'name': 'Caffeine',
                'molecular_formula': 'C8H10N4O2',
                'molecular_weight': 194.19,
                'cas_number': '58-08-2',
                'smiles': 'CN1C=NC2=C1C(=O)N(C(=O)N2C)C',
                'description': 'Central nervous system stimulant',
                'clinical_phase': 'Approved',
                'mechanism_of_action': 'Adenosine receptor antagonist',
                'therapeutic_areas': ['Neurology'],
                'biochemical_group': 'Alkaloids'
            },
            {
                'name': 'Glucose',
                'molecular_formula': 'C6H12O6',
                'molecular_weight': 180.16,
                'cas_number': '50-99-7',
                'smiles': 'C(C1C(C(C(C(O1)O)O)O)O)O',
                'description': 'Primary energy source for cells',
                'clinical_phase': 'Approved',
                'mechanism_of_action': 'Energy substrate',
                'therapeutic_areas': ['Metabolic Disorders'],
                'biochemical_group': 'Carbohydrates'
            },
            {
                'name': 'Insulin',
                'molecular_formula': 'C257H383N65O77S6',
                'molecular_weight': 5808.0,
                'cas_number': '9004-10-8',
                'smiles': None,  # Too complex for SMILES
                'description': 'Hormone that regulates blood glucose levels',
                'clinical_phase': 'Approved',
                'mechanism_of_action': 'Insulin receptor agonist',
                'therapeutic_areas': ['Metabolic Disorders', 'Endocrinology'],
                'biochemical_group': 'Proteins'
            },
            {
                'name': 'Penicillin G',
                'molecular_formula': 'C16H18N2O4S',
                'molecular_weight': 334.39,
                'cas_number': '61-33-6',
                'smiles': 'CC1(C(N2C(S1)C(C2=O)NC(=O)CC3=CC=CC=C3)C(=O)O)C',
                'description': 'Beta-lactam antibiotic',
                'clinical_phase': 'Approved',
                'mechanism_of_action': 'Cell wall synthesis inhibitor',
                'therapeutic_areas': ['Infectious Diseases'],
                'biochemical_group': 'Beta-lactams'
            }
        ]
        
        for compound_data in sample_compounds_data:
            # Check if compound already exists
            existing_compound = Compound.query.filter_by(name=compound_data['name']).first()
            if existing_compound:
                continue
                
            # Create compound
            compound = Compound(
                name=compound_data['name'],
                molecular_formula=compound_data['molecular_formula'],
                molecular_weight=compound_data['molecular_weight'],
                cas_number=compound_data['cas_number'],
                smiles=compound_data['smiles'],
                description=compound_data['description'],
                clinical_phase=compound_data['clinical_phase'],
                mechanism_of_action=compound_data['mechanism_of_action'],
                created_by='seed'
            )
            
            # Add biochemical group relationship
            biochemical_group = BiochemicalGroup.query.filter_by(name=compound_data['biochemical_group']).first()
            if biochemical_group:
                compound.biochemical_group = biochemical_group
            
            # Add therapeutic area relationships
            for area_name in compound_data['therapeutic_areas']:
                therapeutic_area = TherapeuticArea.query.filter_by(name=area_name).first()
                if therapeutic_area:
                    compound.therapeutic_areas.append(therapeutic_area)
            
            # Calculate sync hash
            compound.update_sync_hash()
            
            db.session.add(compound)
        
        db.session.commit()
    click.echo('Database seeded successfully!')

@cli.command('import-compounds')
@click.option('--file', help='JSON file containing compounds to import')
def import_compounds_command(file):
    """Import compounds from a JSON file."""
    if not file:
        click.echo('Please specify a file with --file option')
        return
    
    try:
        with open(file, 'r') as f:
            compounds_data = json.load(f)
        
        imported_count = 0
        app_instance = create_app()
        with app_instance.app_context():
            from models import db, Compound, BiochemicalGroup, TherapeuticArea, Disease, Study # Import models here
            for compound_data in compounds_data:
                # Check if compound already exists
                existing_compound = Compound.query.filter_by(name=compound_data['name']).first()
                if existing_compound:
                    continue
                    
                # Create compound
                compound = Compound(
                    name=compound_data.get('name'),
                    molecular_formula=compound_data.get('molecular_formula'),
                    molecular_weight=compound_data.get('molecular_weight'),
                    cas_number=compound_data.get('cas_number'),
                    smiles=compound_data.get('smiles'),
                    description=compound_data.get('description'),
                    clinical_phase=compound_data.get('clinical_phase'),
                    mechanism_of_action=compound_data.get('mechanism_of_action'),
                    created_by='import'
                )
                
                # Add biochemical group relationship
                if 'biochemical_group' in compound_data:
                    biochemical_group = BiochemicalGroup.query.filter_by(name=compound_data['biochemical_group']).first()
                    if biochemical_group:
                        compound.biochemical_group = biochemical_group
                
                # Add therapeutic area relationships
                if 'therapeutic_areas' in compound_data:
                    for area_name in compound_data['therapeutic_areas']:
                        therapeutic_area = TherapeuticArea.query.filter_by(name=area_name).first()
                        if therapeutic_area:
                            compound.therapeutic_areas.append(therapeutic_area)
                
                compound.update_sync_hash()
                db.session.add(compound)
                imported_count += 1
            
            db.session.commit()
        click.echo(f'Successfully imported {imported_count} compounds from {file}!')
        
    except FileNotFoundError:
        click.echo(f'File {file} not found!')
    except json.JSONDecodeError:
        click.echo(f'Invalid JSON in file {file}!')
    except Exception as e:
        click.echo(f'Error importing compounds: {str(e)}')

@cli.command('db-stats')
def db_stats_command():
    """Show database statistics."""
    app_instance = create_app()
    with app_instance.app_context():
        from models import db, Compound, BiochemicalGroup, TherapeuticArea, Disease, Study # Import models here
        try:
            # Get counts
            compounds_count = Compound.query.count()
            groups_count = BiochemicalGroup.query.count()
            therapeutic_areas_count = TherapeuticArea.query.count()
            
            # Get compounds by clinical phase
            from sqlalchemy import func
            phase_stats = db.session.query(
                Compound.clinical_phase, 
                func.count(Compound.id)
            ).group_by(Compound.clinical_phase).all()
            
            # Get compounds by biochemical group
            group_stats = db.session.query(
                BiochemicalGroup.name, 
                func.count(Compound.id)
            ).join(Compound, BiochemicalGroup.id == Compound.biochemical_group_id, isouter=True).group_by(BiochemicalGroup.name).all()
            
            click.echo('\n=== Database Statistics ===')
            click.echo(f'Total Compounds: {compounds_count}')
            click.echo(f'Biochemical Groups: {groups_count}')
            click.echo(f'Therapeutic Areas: {therapeutic_areas_count}')
            
            click.echo('\nCompounds by Clinical Phase:')
            for phase, count in phase_stats:
                click.echo(f'  {phase or "Unknown"}: {count}')
            
            click.echo('\nCompounds by Biochemical Group:')
            for group, count in group_stats:
                click.echo(f'  {group}: {count}')
            
        except Exception as e:
            click.echo(f'Error getting database stats: {str(e)}')

@cli.command('reset-db')
def reset_db_command():
    """Reset the database (drop all tables and recreate)."""
    if click.confirm('Are you sure you want to reset the database? This will delete all data!'):
        click.echo('Resetting database...')
        app_instance = create_app()
        with app_instance.app_context():
            from models import db, Compound, BiochemicalGroup, TherapeuticArea, Disease, Study # Import models here
            db.drop_all()
            db.create_all()
        click.echo('Database reset complete!')
    else:
        click.echo('Database reset cancelled.')

# Entry point for running the Flask app
if __name__ == '__main__':
    # Create the app instance for the server
    app = create_app()
    
    debug = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Starting {app.config.get('APPLICATION_NAME', 'ModularNucleoid P2P Demo')} on http://0.0.0.0:{port}")
    app.run(debug=debug, port=port, host='0.0.0.0')
