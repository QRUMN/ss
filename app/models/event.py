from . import db, generate_uuid
from datetime import datetime

class Venue(db.Model):
    __tablename__ = 'venues'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer)
    events = db.relationship('Event', backref='venue_info', lazy='dynamic')

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    description = db.Column(db.Text)
    flyer_url = db.Column(db.String(255))
    venue_id = db.Column(db.String(36), db.ForeignKey('venues.id'), nullable=False)
    promoter_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('draft', 'published', 'cancelled', name='event_status'), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Features
    has_guestlist = db.Column(db.Boolean, default=False)
    has_table_service = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    
    # Relationships
    ticket_tiers = db.relationship('TicketTier', backref='event', lazy='dynamic')
    table_reservations = db.relationship('TableReservation', backref='event', lazy='dynamic')
    
    @property
    def is_upcoming(self):
        return datetime.combine(self.date, self.start_time) > datetime.utcnow()
    
    @property
    def is_sold_out(self):
        return all(tier.is_sold_out for tier in self.ticket_tiers)
    
    def get_available_tables(self):
        return [r for r in self.table_reservations if r.status == 'available']
    
    def __repr__(self):
        return f'<Event {self.title} on {self.date}>'
