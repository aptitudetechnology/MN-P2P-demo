"""
Database models for ModularNucleoid P2P Demo
SQLAlchemy models for compounds, biochemical groups, and related entities
"""
#from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Initialize db - this will be configured by app.py
#db = SQLAlchemy()

# Association tables for many-to-many relationships
compound_therapeutic_areas = db.Table('compound_therapeutic_areas',
    db.Column('compound_id', db.Integer, db.ForeignKey('compounds.id'), primary_key=True),
    db.Column('therapeutic_area_id', db.Integer, db.ForeignKey('therapeutic_areas.id'), primary_key=True)
)

compound_diseases = db.Table('compound_diseases',
    db.Column('compound_id', db.Integer, db.ForeignKey('compounds.id'), primary_key=True),
    db.Column('disease_id', db.Integer, db.ForeignKey('diseases.id'), primary_key=True)
)

compound_studies = db.Table('compound_studies',
    db.Column('compound_id', db.Integer, db.ForeignKey('compounds.id'), primary_key=True),
    db.Column('study_id', db.Integer, db.ForeignKey('studies.id'), primary_key=True)
)

class BiochemicalGroup(db.Model):
    """Biochemical groups for the periodic table interface"""
    __tablename__ = 'biochemical_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    color = db.Column(db.String(7), nullable=False)  # Hex color code
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    compounds = db.relationship('Compound', backref='biochemical_group', lazy='dynamic')
    
    def __repr__(self):
        return f'<BiochemicalGroup {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'color': self.color,
            'description': self.description,
            'compound_count': self.compounds.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TherapeuticArea(db.Model):
    """Therapeutic areas for compound classification"""
    __tablename__ = 'therapeutic_areas'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TherapeuticArea {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Disease(db.Model):
    """Diseases that compounds may treat"""
    __tablename__ = 'diseases'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    icd_code = db.Column(db.String(20))  # ICD-10 code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Disease {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icd_code': self.icd_code,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Study(db.Model):
    """Clinical studies or research papers"""
    __tablename__ = 'studies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    study_type = db.Column(db.String(50))  # 'clinical_trial', 'preclinical', 'research_paper'
    phase = db.Column(db.String(20))  # For clinical trials: Phase I, II, III, IV
    status = db.Column(db.String(50))  # 'ongoing', 'completed', 'terminated'
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    principal_investigator = db.Column(db.String(200))
    institution = db.Column(db.String(200))
    pubmed_id = db.Column(db.String(20))
    doi = db.Column(db.String(100))
    abstract = db.Column(db.Text)
    results_summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Study {self.title[:50]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'study_type': self.study_type,
            'phase': self.phase,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'principal_investigator': self.principal_investigator,
            'institution': self.institution,
            'pubmed_id': self.pubmed_id,
            'doi': self.doi,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Compound(db.Model):
    """Main compound model with comprehensive properties"""
    __tablename__ = 'compounds'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True, index=True)
    molecular_formula = db.Column(db.String(100), index=True)
    molecular_weight = db.Column(db.Float, index=True)
    cas_number = db.Column(db.String(20), unique=True, index=True)
    iupac_name = db.Column(db.String(500))
    smiles = db.Column(db.Text)  # SMILES notation
    inchi = db.Column(db.Text)   # InChI string
    inchi_key = db.Column(db.String(100), index=True)  # InChI Key
    
    # Alternative names stored as JSON
    alternative_names = db.Column(db.JSON)
    
    # Physical properties
    melting_point = db.Column(db.Float)  # Celsius
    boiling_point = db.Column(db.Float)  # Celsius
    density = db.Column(db.Float)        # g/cm³
    solubility = db.Column(db.Text)      # Solubility description
    
    # Chemical properties
    ph = db.Column(db.Float)
    pka = db.Column(db.Float)
    logp = db.Column(db.Float)  # Partition coefficient
    
    # Biological properties
    bioavailability = db.Column(db.Float)  # Percentage
    half_life = db.Column(db.Float)        # Hours
    mechanism_of_action = db.Column(db.Text)
    target_proteins = db.Column(db.JSON)   # List of target proteins
    
    # Clinical information
    clinical_phase = db.Column(db.String(50), index=True)  # Preclinical, Phase I, II, III, Approved
    indication = db.Column(db.Text)
    contraindications = db.Column(db.Text)
    side_effects = db.Column(db.JSON)      # List of side effects
    
    # Research information
    description = db.Column(db.Text)
    research_priority = db.Column(db.String(20), default='medium')  # low, medium, high
    source = db.Column(db.String(100))     # Natural, synthetic, etc.
    
    # Relationships
    biochemical_group_id = db.Column(db.Integer, db.ForeignKey('biochemical_groups.id'), index=True)
    
    # Many-to-many relationships
    therapeutic_areas = db.relationship('TherapeuticArea', secondary=compound_therapeutic_areas, 
                                      backref=db.backref('compounds', lazy='dynamic'))
    diseases = db.relationship('Disease', secondary=compound_diseases,
                             backref=db.backref('compounds', lazy='dynamic'))
    studies = db.relationship('Study', secondary=compound_studies,
                            backref=db.backref('compounds', lazy='dynamic'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100))
    
    # Versioning for P2P sync
    version = db.Column(db.Integer, default=1)
    sync_hash = db.Column(db.String(64))  # SHA-256 hash for P2P sync
    
    def __repr__(self):
        return f'<Compound {self.name}>'
    
    def calculate_sync_hash(self):
        """Calculate hash for P2P synchronization"""
        import hashlib
        data = {
            'name': self.name,
            'molecular_formula': self.molecular_formula,
            'molecular_weight': self.molecular_weight,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def update_sync_hash(self):
        """Update sync hash and increment version"""
        self.sync_hash = self.calculate_sync_hash()
        self.version += 1
    
    def to_dict(self, include_relationships=True):
        """Convert compound to dictionary format"""
        base_dict = {
            'id': self.id,
            'name': self.name,
            'molecular_formula': self.molecular_formula,
            'molecular_weight': self.molecular_weight,
            'cas_number': self.cas_number,
            'iupac_name': self.iupac_name,
            'smiles': self.smiles,
            'inchi': self.inchi,
            'inchi_key': self.inchi_key,
            'alternative_names': self.alternative_names,
            
            # Physical properties
            'melting_point': self.melting_point,
            'boiling_point': self.boiling_point,
            'density': self.density,
            'solubility': self.solubility,
            
            # Chemical properties
            'ph': self.ph,
            'pka': self.pka,
            'logp': self.logp,
            
            # Biological properties
            'bioavailability': self.bioavailability,
            'half_life': self.half_life,
            'mechanism_of_action': self.mechanism_of_action,
            'target_proteins': self.target_proteins,
            
            # Clinical information
            'clinical_phase': self.clinical_phase,
            'indication': self.indication,
            'contraindications': self.contraindications,
            'side_effects': self.side_effects,
            
            # Research information
            'description': self.description,
            'research_priority': self.research_priority,
            'source': self.source,
            
            # Metadata
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'version': self.version,
            'sync_hash': self.sync_hash
        }
        
        if include_relationships:
            base_dict.update({
                'biochemical_group': self.biochemical_group.to_dict() if self.biochemical_group else None,
                'therapeutic_areas': [ta.to_dict() for ta in self.therapeutic_areas],
                'diseases': [d.to_dict() for d in self.diseases],
                'studies_count': self.studies.count()
            })
        
        return base_dict
    
    @classmethod
    def search(cls, query, filters=None):
        """Search compounds with filters"""
        search_query = cls.query
        
        if query:
            search_terms = query.split()
            for term in search_terms:
                search_query = search_query.filter(
                    db.or_(
                        cls.name.ilike(f'%{term}%'),
                        cls.molecular_formula.ilike(f'%{term}%'),
                        cls.description.ilike(f'%{term}%'),
                        cls.mechanism_of_action.ilike(f'%{term}%')
                    )
                )
        
        if filters:
            if 'biochemical_group' in filters:
                search_query = search_query.filter(
                    cls.biochemical_group_id == filters['biochemical_group']
                )
            
            if 'clinical_phase' in filters:
                search_query = search_query.filter(
                    cls.clinical_phase == filters['clinical_phase']
                )
            
            if 'molecular_weight_range' in filters:
                min_mw, max_mw = filters['molecular_weight_range']
                search_query = search_query.filter(
                    cls.molecular_weight.between(min_mw, max_mw)
                )
        
        return search_query

class CompoundProperty(db.Model):
    """Additional properties for compounds (extensible)"""
    __tablename__ = 'compound_properties'
    
    id = db.Column(db.Integer, primary_key=True)
    compound_id = db.Column(db.Integer, db.ForeignKey('compounds.id'), nullable=False)
    property_type = db.Column(db.String(100), nullable=False, index=True)
    property_value = db.Column(db.Text, nullable=False)
    units = db.Column(db.String(50))
    confidence = db.Column(db.Float)  # 0.0 to 1.0
    source = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    compound = db.relationship('Compound', backref=db.backref('properties', lazy='dynamic'))
    
    def __repr__(self):
        return f'<CompoundProperty {self.property_type}: {self.property_value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'property_type': self.property_type,
            'property_value': self.property_value,
            'units': self.units,
            'confidence': self.confidence,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }