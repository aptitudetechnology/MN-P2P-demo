# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import hashlib
import json

# Initialize SQLAlchemy here, but don't attach to app yet.
# This allows it to be imported by other modules without circular dependencies.
db = SQLAlchemy()

# Association table for Compound and TherapeuticArea (Many-to-Many)
compound_therapeutic_area = db.Table(
    'compound_therapeutic_area',
    db.Column('compound_id', db.Integer, db.ForeignKey('compound.id'), primary_key=True),
    db.Column('therapeutic_area_id', db.Integer, db.ForeignKey('therapeutic_area.id'), primary_key=True)
)

class Compound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    molecular_formula = db.Column(db.String(255))
    molecular_weight = db.Column(db.Float)
    cas_number = db.Column(db.String(50), unique=True)
    smiles = db.Column(db.Text)
    description = db.Column(db.Text)
    clinical_phase = db.Column(db.String(50)) # e.g., 'Discovery', 'Preclinical', 'Phase 1', 'Approved'
    mechanism_of_action = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(255))
    sync_hash = db.Column(db.String(64), unique=True) # SHA256 hash for synchronization

    # Relationships
    biochemical_group_id = db.Column(db.Integer, db.ForeignKey('biochemical_group.id'))
    biochemical_group = db.relationship('BiochemicalGroup', backref='compounds')
    
    therapeutic_areas = db.relationship(
        'TherapeuticArea', 
        secondary=compound_therapeutic_area, 
        lazy='subquery', 
        backref=db.backref('compounds', lazy=True)
    )

    def update_sync_hash(self):
        """Generates a SHA256 hash of the compound's key data for synchronization."""
        data_to_hash = {
            'name': self.name,
            'molecular_formula': self.molecular_formula,
            'molecular_weight': self.molecular_weight,
            'cas_number': self.cas_number,
            'smiles': self.smiles,
            'description': self.description,
            'clinical_phase': self.clinical_phase,
            'mechanism_of_action': self.mechanism_of_action,
            'biochemical_group_id': self.biochemical_group_id,
            # Note: For many-to-many relationships like therapeutic_areas,
            # you'd typically include their IDs or names sorted to ensure consistent hash.
            # For simplicity, we'll omit them from the hash for now, but for true sync, they'd be needed.
            'therapeutic_areas': sorted([ta.name for ta in self.therapeutic_areas]) if self.therapeutic_areas else []
        }
        self.sync_hash = hashlib.sha256(json.dumps(data_to_hash, sort_keys=True).encode('utf-8')).hexdigest()

    def __repr__(self):
        return f'<Compound {self.name}>'

class BiochemicalGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    category = db.Column(db.String(255))
    color = db.Column(db.String(7)) # Hex color code
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<BiochemicalGroup {self.name}>'

class TherapeuticArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TherapeuticArea {self.name}>'

class Disease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    therapeutic_area_id = db.Column(db.Integer, db.ForeignKey('therapeutic_area.id'))
    therapeutic_area = db.relationship('TherapeuticArea', backref='diseases')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Disease {self.name}>'

class Study(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50)) # e.g., 'Planned', 'Ongoing', 'Completed', 'Cancelled'
    compound_id = db.Column(db.Integer, db.ForeignKey('compound.id'))
    compound = db.relationship('Compound', backref='studies')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Study {self.title}>'
