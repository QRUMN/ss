from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models.user import User, Post, UserTier
from app import db
from datetime import datetime
import stripe

bp = Blueprint('creator', __name__, url_prefix='/creator')

def creator_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_creator and not current_user.is_admin:
            flash('You need to be an approved creator to access this page', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    if current_user.creator_status == 'approved':
        return redirect(url_for('creator.dashboard'))
    
    if request.method == 'POST':
        current_user.creator_bio = request.form.get('bio')
        current_user.creator_status = 'pending'
        db.session.commit()
        
        flash('Your creator application has been submitted!', 'success')
        return redirect(url_for('members.dashboard'))
    
    return render_template('creator/apply.html')

@bp.route('/dashboard')
@creator_required
def dashboard():
    stats = {
        'total_followers': current_user.followers_count,
        'total_posts': Post.query.filter_by(user_id=current_user.id).count(),
        'total_members': UserTier.query.filter_by(user_id=current_user.id).count(),
        'monthly_revenue': calculate_monthly_revenue(current_user.id)
    }
    
    recent_posts = Post.query.filter_by(user_id=current_user.id)\
        .order_by(Post.created_at.desc()).limit(5).all()
    
    return render_template('creator/dashboard.html',
                         stats=stats,
                         recent_posts=recent_posts)

@bp.route('/posts/new', methods=['GET', 'POST'])
@creator_required
def create_post():
    if request.method == 'POST':
        post = Post(
            user_id=current_user.id,
            title=request.form.get('title'),
            content=request.form.get('content'),
            type=request.form.get('type', 'public'),
            status=request.form.get('status', 'published')
        )
        
        # Handle media uploads
        media_files = request.files.getlist('media')
        if media_files:
            media_urls = upload_media_files(media_files)
            post.media_urls = media_urls
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('creator.dashboard'))
    
    return render_template('creator/create_post.html')

@bp.route('/tiers', methods=['GET', 'POST'])
@creator_required
def manage_tiers():
    if request.method == 'POST':
        tier = UserTier(
            name=request.form.get('name'),
            price=float(request.form.get('price')),
            description=request.form.get('description'),
            features=request.form.getlist('features'),
            event_discount=float(request.form.get('event_discount', 0)),
            exclusive_content=bool(request.form.get('exclusive_content')),
            early_access=bool(request.form.get('early_access')),
            custom_badge=bool(request.form.get('custom_badge')),
            priority_support=bool(request.form.get('priority_support'))
        )
        
        db.session.add(tier)
        db.session.commit()
        
        # Create Stripe product and price
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        product = stripe.Product.create(
            name=tier.name,
            description=tier.description
        )
        
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(tier.price * 100),  # Convert to cents
            currency='usd',
            recurring={'interval': 'month'}
        )
        
        tier.stripe_price_id = price.id
        db.session.commit()
        
        flash('Membership tier created successfully!', 'success')
        return redirect(url_for('creator.manage_tiers'))
    
    tiers = UserTier.query.filter_by(user_id=current_user.id).all()
    return render_template('creator/manage_tiers.html', tiers=tiers)

@bp.route('/analytics')
@creator_required
def analytics():
    # Implement analytics dashboard
    return render_template('creator/analytics.html')

@bp.route('/payout')
@creator_required
def payout_settings():
    if request.method == 'POST':
        # Update payout information (Stripe Connect)
        current_user.payout_info = {
            'account_number': request.form.get('account_number'),
            'routing_number': request.form.get('routing_number'),
            'account_type': request.form.get('account_type')
        }
        db.session.commit()
        
        flash('Payout information updated successfully!', 'success')
        return redirect(url_for('creator.dashboard'))
    
    return render_template('creator/payout_settings.html')

def calculate_monthly_revenue(creator_id):
    # Implement revenue calculation logic
    return 0  # Placeholder

def upload_media_files(files):
    # Implement media upload logic (to S3 or similar)
    return []  # Placeholder
