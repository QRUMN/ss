from . import db, generate_uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class UserTier(db.Model):
    __tablename__ = 'user_tiers'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    features = db.Column(db.JSON)  # List of features as JSON
    is_active = db.Column(db.Boolean, default=True)
    
    # Tier-specific benefits
    event_discount = db.Column(db.Float, default=0.0)  # Percentage as decimal
    exclusive_content = db.Column(db.Boolean, default=False)
    early_access = db.Column(db.Boolean, default=False)
    custom_badge = db.Column(db.Boolean, default=False)
    priority_support = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<UserTier {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    membership_tier = db.Column(db.Enum('free', 'monthly', 'tribe', name='membership_tiers'), default='free')
    role = db.Column(db.Enum('admin', 'promoter', 'staff', 'member', 'creator', name='user_roles'), default='member')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Profile fields
    avatar_url = db.Column(db.String(255))
    bio = db.Column(db.Text)
    phone = db.Column(db.String(20))
    instagram = db.Column(db.String(100))
    location = db.Column(db.String(100))
    
    # Creator fields
    is_creator = db.Column(db.Boolean, default=False)
    creator_bio = db.Column(db.Text)
    creator_status = db.Column(db.Enum('pending', 'approved', 'rejected', name='creator_status'))
    payout_info = db.Column(db.JSON)
    
    # Membership fields
    subscription_id = db.Column(db.String(100))  # Stripe subscription ID
    subscription_status = db.Column(db.String(50))
    subscription_end_date = db.Column(db.DateTime)
    
    # Social features
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    
    # Relationships
    events_promoted = db.relationship('Event', backref='promoter', lazy='dynamic')
    tickets = db.relationship('Ticket', backref='owner', lazy='dynamic')
    reservations = db.relationship('TableReservation', backref='user', lazy='dynamic')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_promoter(self):
        return self.role in ['admin', 'promoter']
    
    def get_discount_rate(self):
        if self.membership_tier == 'monthly':
            return 0.10  # 10% discount
        elif self.membership_tier == 'tribe':
            return 0.20  # 20% discount
        return 0.0
    
    def __repr__(self):
        return f'<User {self.name}>'

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Post type and visibility
    type = db.Column(db.Enum('public', 'members', 'tribe', name='post_types'), default='public')
    status = db.Column(db.Enum('draft', 'published', 'archived', name='post_status'), default='draft')
    
    # Media
    media_urls = db.Column(db.JSON)  # List of media URLs as JSON
    
    # Engagement
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Post {self.title}>'

class UserFollower(db.Model):
    __tablename__ = 'user_followers'
    
    follower_id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserFollower {self.follower_id} -> {self.followed_id}>'
