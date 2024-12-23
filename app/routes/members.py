from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models.user import User
from app.models.ticket import Ticket
from app.models.reservation import TableReservation
from app import db

bp = Blueprint('members', __name__, url_prefix='/members')

@bp.route('/dashboard')
@login_required
def dashboard():
    upcoming_tickets = Ticket.query.join(Ticket.tier)\
        .filter(Ticket.user_id == current_user.id, Ticket.status == 'active')\
        .order_by(Ticket.purchase_date.desc()).limit(5).all()
    
    upcoming_reservations = TableReservation.query\
        .filter(TableReservation.user_id == current_user.id,
                TableReservation.status.in_(['pending', 'confirmed']))\
        .order_by(TableReservation.created_at.desc()).limit(5).all()
    
    return render_template('members/dashboard.html',
                         tickets=upcoming_tickets,
                         reservations=upcoming_reservations)

@bp.route('/tickets')
@login_required
def tickets():
    page = request.args.get('page', 1, type=int)
    tickets = Ticket.query.filter_by(user_id=current_user.id)\
        .order_by(Ticket.purchase_date.desc())\
        .paginate(page=page, per_page=10)
    
    return render_template('members/tickets.html', tickets=tickets)

@bp.route('/reservations')
@login_required
def reservations():
    page = request.args.get('page', 1, type=int)
    reservations = TableReservation.query.filter_by(user_id=current_user.id)\
        .order_by(TableReservation.created_at.desc())\
        .paginate(page=page, per_page=10)
    
    return render_template('members/reservations.html', reservations=reservations)

@bp.route('/membership', methods=['GET', 'POST'])
@login_required
def membership():
    if request.method == 'POST':
        tier = request.form.get('tier')
        if tier in ['monthly', 'tribe']:
            # Here you would typically integrate with Stripe for subscription
            current_user.membership_tier = tier
            db.session.commit()
            flash(f'Successfully upgraded to {tier} membership!', 'success')
            return redirect(url_for('members.dashboard'))
    
    return render_template('members/membership.html')

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        if 'password' in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            
            if current_user.check_password(current_password):
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password updated successfully!', 'success')
            else:
                flash('Current password is incorrect', 'error')
        
        elif 'notifications' in request.form:
            # Update notification preferences
            pass
    
    return render_template('members/settings.html')
