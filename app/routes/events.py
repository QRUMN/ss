from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models.event import Event, Venue
from app.models.ticket import TicketTier, Ticket
from app.models.reservation import TableReservation
from app import db
from datetime import datetime

bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    events = Event.query.filter_by(status='published')\
        .order_by(Event.date.asc())\
        .paginate(page=page, per_page=current_app.config['EVENTS_PER_PAGE'])
    return render_template('events/index.html', events=events)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_promoter:
        flash('You do not have permission to create events', 'error')
        return redirect(url_for('events.index'))
    
    if request.method == 'POST':
        venue = Venue(
            name=request.form.get('venue_name'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            zip_code=request.form.get('zip_code')
        )
        db.session.add(venue)
        
        event = Event(
            title=request.form.get('title'),
            date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
            start_time=datetime.strptime(request.form.get('start_time'), '%H:%M').time(),
            end_time=datetime.strptime(request.form.get('end_time'), '%H:%M').time(),
            description=request.form.get('description'),
            venue_id=venue.id,
            promoter_id=current_user.id,
            has_guestlist=bool(request.form.get('has_guestlist')),
            has_table_service=bool(request.form.get('has_table_service'))
        )
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.manage', event_id=event.id))
    
    return render_template('events/create.html')

@bp.route('/<event_id>')
def detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('events/detail.html', event=event)

@bp.route('/<event_id>/manage')
@login_required
def manage(event_id):
    event = Event.query.get_or_404(event_id)
    if event.promoter_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to manage this event', 'error')
        return redirect(url_for('events.detail', event_id=event_id))
    
    return render_template('events/manage.html', event=event)

@bp.route('/<event_id>/tickets/purchase', methods=['POST'])
@login_required
def purchase_tickets(event_id):
    event = Event.query.get_or_404(event_id)
    tier_id = request.form.get('tier_id')
    quantity = int(request.form.get('quantity', 1))
    
    tier = TicketTier.query.get_or_404(tier_id)
    if tier.event_id != event.id:
        flash('Invalid ticket tier', 'error')
        return redirect(url_for('events.detail', event_id=event_id))
    
    if tier.is_sold_out:
        flash('This ticket tier is sold out', 'error')
        return redirect(url_for('events.detail', event_id=event_id))
    
    price = tier.get_price_for_member(current_user)
    
    # Here you would typically integrate with Stripe for payment
    # For now, we'll just create the tickets
    for _ in range(quantity):
        ticket = Ticket(
            tier_id=tier.id,
            user_id=current_user.id,
            purchase_price=price
        )
        db.session.add(ticket)
        tier.sold_count += 1
    
    db.session.commit()
    flash(f'Successfully purchased {quantity} tickets!', 'success')
    return redirect(url_for('events.detail', event_id=event_id))
