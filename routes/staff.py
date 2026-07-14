from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, Trek, Booking
from functools import wraps

staff_bp = Blueprint('staff', __name__)

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'staff':
            return redirect(url_for('auth.login'))
        if current_user.status != 'active':
            return render_template('staff/pending.html')
        return f(*args, **kwargs)
    return decorated_function


@staff_bp.route('/dashboard')
@login_required
@staff_required
def dashboard():
    assigned_treks = Trek.query.filter_by(staff_id=current_user.id).all()
    return render_template('staff/dashboard.html', treks=assigned_treks)


# @staff_bp.route('/trek/<int:trek_id>/update', methods=['POST'])
# @login_required
# @staff_required
# def update_trek(trek_id):
#     trek = Trek.query.get_or_404(trek_id)
#     if trek.staff_id != current_user.id:
#         return redirect(url_for('staff.dashboard'))
#     trek.available_slots = int(request.form.get('available_slots'))
#     trek.status = request.form.get('status')
#     db.session.commit()
#     return redirect(url_for('staff.dashboard'))


@staff_bp.route('/trek/<int:trek_id>/participants')
@login_required
@staff_required
def participants(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    return render_template('staff/participants.html', trek=trek, bookings=bookings)


@staff_bp.route('/trek/<int:trek_id>/update', methods=['POST'])
@login_required
@staff_required
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.staff_id != current_user.id:
        return redirect(url_for('staff.dashboard'))
    
    trek.available_slots = int(request.form.get('available_slots'))
    trek.status = request.form.get('status')
    
    # jab trek Complete ho toh saari bookings bhi Complete
    if trek.status == 'Completed':
        bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
        for booking in bookings:
            booking.status = 'Completed'
    
    db.session.commit()
    return redirect(url_for('staff.dashboard'))


@staff_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@staff_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.phone = request.form.get('phone')
        db.session.commit()
        print("Profile updated!")
        return redirect(url_for('staff.profile'))
    return render_template('staff/profile.html')