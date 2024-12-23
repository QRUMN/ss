from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User
from app.models.event import Event
from app.models.ticket import TicketTier
from app import db
from functools import wraps

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this area', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def index():
    stats = {
        'total_users': User.query.count(),
        'total_events': Event.query.count(),
        'active_events': Event.query.filter_by(status='published').count(),
        'monthly_members': User.query.filter_by(membership_tier='monthly').count(),
        'tribe_members': User.query.filter_by(membership_tier='tribe').count()
    }
    return render_template('admin/index.html', stats=stats)

@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users)

@bp.route('/users/<user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.membership_tier = request.form.get('membership_tier')
        user.role = request.form.get('role')
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=user)

@bp.route('/events')
@login_required
@admin_required
def events():
    page = request.args.get('page', 1, type=int)
    events = Event.query.paginate(page=page, per_page=20)
    return render_template('admin/events.html', events=events)

@bp.route('/events/<event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.status = request.form.get('status')
        event.is_featured = bool(request.form.get('is_featured'))
        
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('admin.events'))
    
    return render_template('admin/edit_event.html', event=event)

@bp.route('/reports')
@login_required
@admin_required
def reports():
    # Add your reporting logic here
    return render_template('admin/reports.html')
