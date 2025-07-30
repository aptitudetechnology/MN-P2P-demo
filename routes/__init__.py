# routes/__init__.py

"""
Routes package for organized route handling
"""

def register_blueprints(app):
    """
    Registers all blueprints with the Flask application instance.
    Imports blueprints locally to avoid circular import issues.
    """
    # Import blueprints here, inside the function, to prevent circular imports
    from .main import main_bp
    from .api import api_bp # Uncomment if you have an api blueprint
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api') # Register with a prefix if needed
