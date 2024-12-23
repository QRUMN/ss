from . import db, generate_uuid
from datetime import datetime

class TicketTier(db.Model):
    __tablename__ = 'ticket_tiers'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    event_id = db.Column(db.String(36), db.ForeignKey('events.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sold_count = db.Column(db.Integer, default=0)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    # Member discounts
    monthly_discount = db.Column(db.Float, default=0.0)  # Percentage as decimal
    tribe_discount = db.Column(db.Float, default=0.0)    # Percentage as decimal
    
    is_vip = db.Column(db.Boolean, default=False)
    perks = db.Column(db.JSON)  # List of perks as JSON
    
    # Relationships
    tickets = db.relationship('Ticket', backref='tier', lazy='dynamic')
    
    @property
    def is_sold_out(self):
        return self.sold_count >= self.quantity
    
    @property
    def available_quantity(self):
        return self.quantity - self.sold_count
    
    def get_price_for_member(self, user):
        if not user:
            return self.price
        
        if user.membership_tier == 'tribe':
            return self.price * (1 - self.tribe_discount)
        elif user.membership_tier == 'monthly':
            return self.price * (1 - self.monthly_discount)
        return self.price

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    tier_id = db.Column(db.String(36), db.ForeignKey('ticket_tiers.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('active', 'used', 'refunded', 'cancelled', name='ticket_status'), default='active')
    qr_code = db.Column(db.String(255))  # URL to QR code image
    
    def mark_as_used(self):
        self.status = 'used'
        db.session.commit()
    
    def generate_qr_code(self):
        # Implementation for QR code generation
        pass
    
    def __repr__(self):
        return f'<Ticket {self.id} for {self.tier.event.title}>'
