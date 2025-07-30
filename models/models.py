# config.py - Application Configuration
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///compounds.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Pagination
    COMPOUNDS_PER_PAGE = 12
    STUDIES_PER_PAGE = 10
    
    # Search configuration
    SEARCH_RESULTS_PER_PAGE = 20
    MAX_SEARCH_RESULTS = 1000
    
    # P2P Network configuration
    P2P_PORT = int(os.environ.get('P2P_PORT', 8001))
    P2P_HOST = os.environ.get('P2P_HOST', '0.0.0.0')
    P2P_NETWORK_ID = os.environ.get('P2P_NETWORK_ID', 'mn-compounds-network')
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'json', 'csv', 'xlsx', 'sdf', 'mol'}
    
    # Cache configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # API rate limiting
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = '1000/hour'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'compounds_dev.db')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/compounds_prod'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


# app.py - Application Factory
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

from .models import db
from .routes import main
from .config import config

migrate = Migrate()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()

def create_app(config_name=None):
    """Application factory function"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    # Register blueprints
    app.register_blueprint(main)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': str(e.description)
        }), 429
    
    # Context processors
    @app.context_processor
    def inject_config():
        return {
            'config': app.config,
            'get_biochemical_groups': lambda: BiochemicalGroup.query.all(),
            'get_therapeutic_areas': lambda: TherapeuticArea.query.all()
        }
    
    # CLI commands
    @app.cli.command()
    def init_db():
        """Initialize the database"""
        db.create_all()
        print('Database tables created.')
    
    @app.cli.command()
    def seed_db():
        """Seed the database with sample data"""
        from .database_seeder import seed_database
        seed_database()
        print('Database seeded with sample data.')
    
    @app.cli.command()
    def reset_db():
        """Reset the database (WARNING: Destroys all data)"""
        if input('Are you sure you want to reset the database? (yes/no): ') == 'yes':
            db.drop_all()
            db.create_all()
            print('Database reset complete.')
        else:
            print('Database reset cancelled.')
    
    return app


# database_operations.py - Advanced Database Operations
from sqlalchemy import text, func, case
from sqlalchemy.orm import joinedload
from .models import db, Compound, BiochemicalGroup, TherapeuticArea

class CompoundSearch:
    """Advanced search functionality for compounds"""
    
    @staticmethod
    def search_compounds(query_text, filters=None, sort_by='relevance', page=1, per_page=20):
        """
        Advanced compound search with full-text search capabilities
        """
        base_query = Compound.query.options(
            joinedload(Compound.biochemical_group),
            joinedload(Compound.therapeutic_areas)
        )
        
        # Full-text search
        if query_text:
            search_terms = query_text.split()
            search_conditions = []
            
            for term in search_terms:
                term_filter = db.or_(
                    Compound.name.ilike(f'%{term}%'),
                    Compound.molecular_formula.ilike(f'%{term}%'),
                    Compound.description.ilike(f'%{term}%'),
                    Compound.iupac_name.ilike(f'%{term}%'),
                    Compound.alternative_names.ilike(f'%{term}%')
                )
                search_conditions.append(term_filter)
            
            if search_conditions:
                base_query = base_query.filter(db.and_(*search_conditions))
        
        # Apply filters
        if filters:
            if filters.get('biochemical_group'):
                base_query = base_query.filter(
                    Compound.biochemical_group_id == filters['biochemical_group']
                )
            
            if filters.get('therapeutic_area'):
                base_query = base_query.join(Compound.therapeutic_areas).filter(
                    TherapeuticArea.id == filters['therapeutic_area']
                )
            
            if filters.get('molecular_weight_range'):
                min_mw, max_mw = filters['molecular_weight_range']
                base_query = base_query.filter(
                    Compound.molecular_weight.between(min_mw, max_mw)
                )
            
            if filters.get('clinical_phase'):
                base_query = base_query.filter(
                    Compound.clinical_phase == filters['clinical_phase']
                )
        
        # Sorting
        if sort_by == 'relevance' and query_text:
            # Calculate relevance score
            relevance_score = case([
                (Compound.name.ilike(f'%{query_text}%'), 3),
                (Compound.molecular_formula.ilike(f'%{query_text}%'), 2),
            ], else_=1)
            base_query = base_query.order_by(relevance_score.desc(), Compound.name)
        elif sort_by == 'name':
            base_query = base_query.order_by(Compound.name)
        elif sort_by == 'molecular_weight':
            base_query = base_query.order_by(Compound.molecular_weight)
        elif sort_by == 'created_at':
            base_query = base_query.order_by(Compound.created_at.desc())
        
        # Pagination
        return base_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_search_suggestions(partial_query, limit=10):
        """Get search suggestions based on partial input"""
        suggestions = []
        
        # Name suggestions
        name_matches = db.session.query(Compound.name).filter(
            Compound.name.ilike(f'%{partial_query}%')
        ).limit(limit).all()
        suggestions.extend([match[0] for match in name_matches])
        
        # Formula suggestions
        formula_matches = db.session.query(Compound.molecular_formula).filter(
            Compound.molecular_formula.ilike(f'%{partial_query}%')
        ).limit(limit).all()
        suggestions.extend([match[0] for match in formula_matches if match[0]])
        
        return list(set(suggestions))[:limit]

class CompoundAnalytics:
    """Analytics and statistics for compounds database"""
    
    @staticmethod
    def get_distribution_by_group():
        """Get compound distribution by biochemical group"""
        return db.session.query(
            BiochemicalGroup.name,
            BiochemicalGroup.color,
            func.count(Compound.id).label('count')
        ).join(Compound).group_by(BiochemicalGroup.id).all()
    
    @staticmethod
    def get_molecular_weight_distribution(bins=10):
        """Get molecular weight distribution"""
        min_mw = db.session.query(func.min(Compound.molecular_weight)).scalar() or 0
        max_mw = db.session.query(func.max(Compound.molecular_weight)).scalar() or 1000
        
        bin_size = (max_mw - min_mw) / bins
        distribution = []
        
        for i in range(bins):
            range_start = min_mw + (i * bin_size)
            range_end = min_mw + ((i + 1) * bin_size)
            
            count = db.session.query(func.count(Compound.id)).filter(
                Compound.molecular_weight.between(range_start, range_end)
            ).scalar()
            
            distribution.append({
                'range': f'{range_start:.0f}-{range_end:.0f}',
                'count': count
            })
        
        return distribution
    
    @staticmethod
    def get_recent_activity(days=30):
        """Get recent database activity"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return {
            'new_compounds': Compound.query.filter(
                Compound.created_at >= cutoff_date
            ).count(),
            'updated_compounds': Compound.query.filter(
                Compound.updated_at >= cutoff_date
            ).count()
        }

class CompoundExporter:
    """Export compound data in various formats"""
    
    @staticmethod
    def export_to_json(compound_ids=None):
        """Export compounds to JSON format"""
        query = Compound.query.options(
            joinedload(Compound.biochemical_group),
            joinedload(Compound.therapeutic_areas),
            joinedload(Compound.diseases)
        )
        
        if compound_ids:
            query = query.filter(Compound.id.in_(compound_ids))
        
        compounds = query.all()
        
        export_data = {
            'metadata': {
                'exported_at': datetime.utcnow().isoformat(),
                'total_compounds': len(compounds),
                'format_version': '1.0'
            },
            'compounds': [compound.to_dict() for compound in compounds]
        }
        
        return export_data
    
    @staticmethod
    def export_to_csv(compound_ids=None):
        """Export compounds to CSV format"""
        import csv
        import io
        
        query = Compound.query.options(joinedload(Compound.biochemical_group))
        if compound_ids:
            query = query.filter(Compound.id.in_(compound_ids))
        
        compounds = query.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'ID', 'Name', 'Molecular Formula', 'Molecular Weight',
            'CAS Number', 'Biochemical Group', 'Description', 'Created At'
        ])
        
        # Data rows
        for compound in compounds:
            writer.writerow([
                compound.id,
                compound.name,
                compound.molecular_formula,
                compound.molecular_weight,
                compound.cas_number,
                compound.biochemical_group.name if compound.biochemical_group else '',
                compound.description,
                compound.created_at.isoformat() if compound.created_at else ''
            ])
        
        return output.getvalue()


# p2p_integration.py - P2P Network Integration
import asyncio
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from flask import current_app

@dataclass
class P2PMessage:
    """Structure for P2P network messages"""
    message_type: str
    sender_id: str
    timestamp: str
    data: Dict
    signature: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)
    
    def calculate_hash(self):
        """Calculate message hash for integrity verification"""
        message_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(message_str.encode()).hexdigest()

class CompoundP2PManager:
    """Manages P2P sharing of compound data"""
    
    def __init__(self, node_id: str, network_config: Dict):
        self.node_id = node_id
        self.network_config = network_config
        self.peers = set()
        self.shared_compounds = {}
        
    async def share_compound(self, compound_data: Dict) -> bool:
        """Share compound data across P2P network"""
        try:
            message = P2PMessage(
                message_type="compound_share",
                sender_id=self.node_id,
                timestamp=datetime.utcnow().isoformat(),
                data={
                    "compound": compound_data,
                    "action": "share"
                }
            )
            
            # Store locally
            compound_hash = message.calculate_hash()
            self.shared_compounds[compound_hash] = compound_data
            
            # Broadcast to peers
            await self._broadcast_message(message)
            
            current_app.logger.info(f"Compound {compound_data.get('name')} shared via P2P")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to share compound: {str(e)}")
            return False
    
    async def request_compound(self, compound_id: str) -> Optional[Dict]:
        """Request compound data from P2P network"""
        message = P2PMessage(
            message_type="compound_request",
            sender_id=self.node_id,
            timestamp=datetime.utcnow().isoformat(),
            data={
                "compound_id": compound_id,
                "action": "request"
            }
        )
        
        responses = await self._broadcast_message_and_wait(message, timeout=10)
        
        # Return first valid response
        for response in responses:
            if response.data.get("compound"):
                return response.data["compound"]
        
        return None
    
    async def sync_database(self) -> Dict:
        """Synchronize local database with P2P network"""
        sync_stats = {
            "requested": 0,
            "received": 0,
            "conflicts": 0,
            "errors": 0
        }
        
        try:
            # Request database metadata from peers
            message = P2PMessage(
                message_type="db_sync_request",
                sender_id=self.node_id,
                timestamp=datetime.utcnow().isoformat(),
                data={"action": "metadata_request"}
            )
            
            peer_responses = await self._broadcast_message_and_wait(message, timeout=30)
            
            # Process responses and identify compounds to sync
            for response in peer_responses:
                peer_compounds = response.data.get("compounds", [])
                for compound_metadata in peer_compounds:
                    if await self._should_sync_compound(compound_metadata):
                        compound_data = await self.request_compound(compound_metadata["id"])
                        if compound_data:
                            await self._merge_compound_data(compound_data)
                            sync_stats["received"] += 1
                        sync_stats["requested"] += 1
            
            return sync_stats
            
        except Exception as e:
            current_app.logger.error(f"Database sync failed: {str(e)}")
            sync_stats["errors"] += 1
            return sync_stats
    
    async def _broadcast_message(self, message: P2PMessage):
        """Broadcast message to all connected peers"""
        for peer in self.peers:
            try:
                await self._send_to_peer(peer, message)
            except Exception as e:
                current_app.logger.warning(f"Failed to send to peer {peer}: {str(e)}")
    
    async def _broadcast_message_and_wait(self, message: P2PMessage, timeout: int = 10) -> List[P2PMessage]:
        """Broadcast message and wait for responses"""
        responses = []
        
        # Implementation would depend on your P2P networking library
        # This is a simplified version
        
        return responses
    
    async def _send_to_peer(self, peer_address: str, message: P2PMessage):
        """Send message to specific peer"""
        # Implementation depends on networking protocol (WebRTC, libp2p, etc.)
        pass
    
    async def _should_sync_compound(self, compound_metadata: Dict) -> bool:
        """Determine if compound should be synced"""
        from .models import Compound
        
        local_compound = Compound.query.filter_by(
            name=compound_metadata.get("name")
        ).first()
        
        if not local_compound:
            return True  # New compound
        
        # Check if remote version is newer
        remote_updated = datetime.fromisoformat(compound_metadata.get("updated_at", "1970-01-01"))
        local_updated = local_compound.updated_at or datetime.min
        
        return remote_updated > local_updated
    
    async def _merge_compound_data(self, compound_data: Dict):
        """Merge compound data into local database"""
        from .models import db, Compound, BiochemicalGroup
        
        try:
            # Find or create compound
            compound = Compound.query.filter_by(name=compound_data["name"]).first()
            
            if not compound:
                # Create new compound
                group = BiochemicalGroup.query.filter_by(
                    code=compound_data.get("biochemical_group", {}).get("code")
                ).first()
                
                compound = Compound(
                    name=compound_data["name"],
                    molecular_formula=compound_data.get("molecular_formula"),
                    molecular_weight=compound_data.get("molecular_weight"),
                    biochemical_group=group,
                    description=compound_data.get("description"),
                    created_by="p2p_sync"
                )
                db.session.add(compound)
            else:
                # Update existing compound
                compound.description = compound_data.get("description", compound.description)
                compound.molecular_weight = compound_data.get("molecular_weight", compound.molecular_weight)
                compound.updated_at = datetime.utcnow()
            
            db.session.commit()
            current_app.logger.info(f"Merged compound: {compound.name}")
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to merge compound data: {str(e)}")
            raise


# api_routes.py - RESTful API endpoints
from flask import Blueprint, request, jsonify
from flask_limiter.util import get_remote_address
from .models import db, Compound, BiochemicalGroup, TherapeuticArea
from .database_operations import CompoundSearch, CompoundAnalytics, CompoundExporter

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/compounds', methods=['GET'])
@limiter.limit("100/minute")
def get_compounds():
    """Get compounds with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Search parameters
        search_query = request.args.get('q', '')
        group_filter = request.args.get('group', '')
        sort_by = request.args.get('sort', 'name')
        
        # Build filters
        filters = {}
        if group_filter:
            group = BiochemicalGroup.query.filter_by(code=group_filter).first()
            if group:
                filters['biochemical_group'] = group.id
        
        # Molecular weight range
        mw_min = request.args.get('mw_min', type=float)
        mw_max = request.args.get('mw_max', type=float)
        if mw_min is not None and mw_max is not None:
            filters['molecular_weight_range'] = (mw_min, mw_max)
        
        # Perform search
        pagination = CompoundSearch.search_compounds(
            search_query, filters, sort_by, page, per_page
        )
        
        # Format response
        compounds_data = []
        for compound in pagination.items:
            compounds_data.append({
                'id': compound.id,
                'name': compound.name,
                'molecular_formula': compound.molecular_formula,
                'molecular_weight': compound.molecular_weight,
                'biochemical_group': {
                    'code': compound.biochemical_group.code,
                    'name': compound.biochemical_group.name,
                    'symbol': compound.biochemical_group.symbol
                } if compound.biochemical_group else None,
                'therapeutic_areas': [
                    {'name': ta.name, 'color': ta.color} 
                    for ta in compound.therapeutic_areas
                ],
                'description': compound.description,
                'created_at': compound.created_at.isoformat() if compound.created_at else None
            })
        
        return jsonify({
            'compounds': compounds_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/compounds/<int:compound_id>', methods=['GET'])
@limiter.limit("200/minute")
def get_compound(compound_id):
    """Get detailed compound information"""
    compound = Compound.query.get_or_404(compound_id)
    
    return jsonify({
        'compound': compound.to_dict(),
        'studies': [
            {
                'id': study.id,
                'title': study.title,
                'journal': study.journal,
                'publication_date': study.publication_date.isoformat() if study.publication_date else None,
                'findings': study.findings
            }
            for study in compound.studies.limit(10)
        ],
        'properties': [
            {
                'type': prop.property_type,
                'value': prop.property_value,
                'units': prop.units,
                'target': prop.target
            }
            for prop in compound.properties
        ]
    })

@api.route('/compounds/<int:compound_id>', methods=['PUT'])
@limiter.limit("10/minute")
def update_compound(compound_id):
    """Update compound information"""
    compound = Compound.query.get_or_404(compound_id)
    data = request.get_json()
    
    try:
        # Update allowed fields
        allowed_fields = [
            'description', 'mechanism_of_action', 'clinical_phase', 
            'research_priority', 'solubility'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(compound, field, data[field])
        
        compound.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Compound updated successfully',
            'compound': compound.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@api.route('/compounds/<int:compound_id>/p2p-share', methods=['POST'])
@limiter.limit("5/minute")
def share_compound_p2p(compound_id):
    """Share compound via P2P network"""
    compound = Compound.query.get_or_404(compound_id)
    
    try:
        # Initialize P2P manager if not exists
        if not hasattr(current_app, 'p2p_manager'):
            from .p2p_integration import CompoundP2PManager
            current_app.p2p_manager = CompoundP2PManager(
                node_id=current_app.config.get('P2P_NODE_ID', 'default-node'),
                network_config=current_app.config.get('P2P_CONFIG', {})
            )
        
        # Share compound data
        compound_data = compound.to_dict()
        success = asyncio.run(current_app.p2p_manager.share_compound(compound_data))
        
        if success:
            return jsonify({
                'message': f'Compound {compound.name} shared via P2P network',
                'compound_id': compound_id
            })
        else:
            return jsonify({'error': 'Failed to share compound'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/analytics/distribution', methods=['GET'])
@limiter.limit("50/minute")
def get_distribution_analytics():
    """Get compound distribution analytics"""
    try:
        group_distribution = CompoundAnalytics.get_distribution_by_group()
        mw_distribution = CompoundAnalytics.get_molecular_weight_distribution()
        
        return jsonify({
            'biochemical_groups': [
                {
                    'name': row.name,
                    'color': row.color,
                    'count': row.count
                }
                for row in group_distribution
            ],
            'molecular_weight_distribution': mw_distribution,
            'recent_activity': CompoundAnalytics.get_recent_activity()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/export', methods=['POST'])
@limiter.limit("5/minute")
def export_compounds():
    """Export compounds in specified format"""
    data = request.get_json()
    compound_ids = data.get('compound_ids', [])
    export_format = data.get('format', 'json').lower()
    
    try:
        if export_format == 'json':
            export_data = CompoundExporter.export_to_json(compound_ids)
            return jsonify(export_data)
        elif export_format == 'csv':
            csv_data = CompoundExporter.export_to_csv(compound_ids)
            response = make_response(csv_data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename=compounds.csv'
            return response
        else:
            return jsonify({'error': 'Unsupported export format'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/search/suggestions', methods=['GET'])
@limiter.limit("100/minute")
def get_search_suggestions():
    """Get search suggestions for autocomplete"""
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify({'suggestions': []})
    
    try:
        suggestions = CompoundSearch.get_search_suggestions(query, limit=10)
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Enhanced CLI commands for database management
# cli_commands.py
import click
from flask.cli import with_appcontext
from .models import db, Compound, BiochemicalGroup
from .database_operations import CompoundAnalytics
from .p2p_integration import CompoundP2PManager

@click.command()
@click.option('--format', default='table', help='Output format (table, json)')
@with_appcontext
def db_stats(format):
    """Display database statistics"""
    try:
        stats = {
            'total_compounds': Compound.query.count(),
            'biochemical_groups': BiochemicalGroup.query.count(),
            'distribution': CompoundAnalytics.get_distribution_by_group(),
            'recent_activity': CompoundAnalytics.get_recent_activity()
        }
        
        if format == 'json':
            click.echo(json.dumps(stats, indent=2, default=str))
        else:
            click.echo(f"Database Statistics:")
            click.echo(f"  Total Compounds: {stats['total_compounds']}")
            click.echo(f"  Biochemical Groups: {stats['biochemical_groups']}")
            click.echo(f"  Recent Activity (30 days):")
            click.echo(f"    New: {stats['recent_activity']['new_compounds']}")
            click.echo(f"    Updated: {stats['recent_activity']['updated_compounds']}")
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@click.command()
@click.option('--file', required=True, help='JSON file containing compound data')
@with_appcontext
def import_compounds(file):
    """Import compounds from JSON file"""
    try:
        import json
        
        with open(file, 'r') as f:
            data = json.load(f)
        
        compounds_data = data.get('compounds', [])
        imported = 0
        errors = 0
        
        for compound_data in compounds_data:
            try:
                # Check if compound already exists
                existing = Compound.query.filter_by(name=compound_data['name']).first()
                if existing:
                    click.echo(f"Skipping existing compound: {compound_data['name']}")
                    continue
                
                # Find biochemical group
                group = BiochemicalGroup.query.filter_by(
                    code=compound_data.get('biochemical_group', {}).get('code')
                ).first()
                
                if not group:
                    click.echo(f"Warning: Biochemical group not found for {compound_data['name']}")
                    continue
                
                # Create compound
                compound = Compound(
                    name=compound_data['name'],
                    molecular_formula=compound_data.get('molecular_formula'),
                    molecular_weight=compound_data.get('molecular_weight'),
                    cas_number=compound_data.get('cas_number'),
                    iupac_name=compound_data.get('iupac_name'),
                    biochemical_group=group,
                    description=compound_data.get('description'),
                    mechanism_of_action=compound_data.get('mechanism_of_action'),
                    source=compound_data.get('source'),
                    created_by='import'
                )
                
                db.session.add(compound)
                imported += 1
                
            except Exception as e:
                errors += 1
                click.echo(f"Error importing {compound_data.get('name', 'unknown')}: {str(e)}")
        
        db.session.commit()
        click.echo(f"Import completed: {imported} compounds imported, {errors} errors")
        
    except Exception as e:
        db.session.rollback()
        click.echo(f"Import failed: {str(e)}", err=True)

@click.command()
@with_appcontext
def p2p_sync():
    """Synchronize database with P2P network"""
    try:
        from flask import current_app
        
        p2p_manager = CompoundP2PManager(
            node_id=current_app.config.get('P2P_NODE_ID', 'cli-node'),
            network_config=current_app.config.get('P2P_CONFIG', {})
        )
        
        click.echo("Starting P2P database synchronization...")
        
        import asyncio
        sync_result = asyncio.run(p2p_manager.sync_database())
        
        click.echo(f"Synchronization completed:")
        click.echo(f"  Requested: {sync_result['requested']}")
        click.echo(f"  Received: {sync_result['received']}")
        click.echo(f"  Conflicts: {sync_result['conflicts']}")
        click.echo(f"  Errors: {sync_result['errors']}")
        
    except Exception as e:
        click.echo(f"P2P sync failed: {str(e)}", err=True)

def register_cli_commands(app):
    """Register all CLI commands with the Flask app"""
    app.cli.add_command(db_stats)
    app.cli.add_command(import_compounds)
    app.cli.add_command(p2p_sync)