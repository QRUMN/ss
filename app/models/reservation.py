from . import db, generate_uuid
from datetime import datetime

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))  # e.g., 'bottle', 'mixer', 'add-on'
    is_available = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Service {self.name}>'

class TableReservation(db.Model):
    __tablename__ = 'table_reservations'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    event_id = db.Column(db.String(36), db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    table_number = db.Column(db.String(20), nullable=False)
    min_spend = db.Column(db.Float, nullable=False)
    deposit_amount = db.Column(db.Float, nullable=False)
    party_size = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('pending', 'confirmed', 'cancelled', 'completed', name='reservation_status'), default='pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    services = db.relationship('ReservationService', backref='reservation', lazy='dynamic')
    
    @property
    def total_spend(self):
        return sum(service.quantity * service.service.price for service in self.services)
    
    def meets_minimum_spend(self):
        return self.total_spend >= self.min_spend
    
    def __repr__(self):
        return f'<TableReservation {self.table_number} for {self.event.title}>'

class ReservationService(db.Model):
    __tablename__ = 'reservation_services'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    reservation_id = db.Column(db.String(36), db.ForeignKey('table_reservations.id'), nullable=False)
    service_id = db.Column(db.String(36), db.ForeignKey('services.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    special_requests = db.Column(db.Text)
    
    # Relationship
    service = db.relationship('Service')
    
    def __repr__(self):
        return f'<ReservationService {self.service.name} x{self.quantity}>'
