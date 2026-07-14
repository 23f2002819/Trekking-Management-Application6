from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, Trek, Booking
from functools import wraps

user_bp = Blueprint('user', __name__)

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'user':
            
            return redirect(url_for('auth.login'))
        if current_user.status == 'blacklisted':
            return redirect(url_for('auth.logout'))
        return f(*args, **kwargs)
    return decorated_function


# @user_bp.route('/dashboard')
# @login_required
# @user_required
# def dashboard():
#     open_treks = Trek.query.filter_by(status='Open').all()
#     my_bookings = Booking.query.filter_by(user_id=current_user.id).all()
#     return render_template('user/dashboard.html', treks=open_treks, bookings=my_bookings)
@user_bp.route('/dashboard')
@login_required
@user_required
def dashboard():
    difficulty = request.args.get('difficulty')
    location = request.args.get('location')

    query = Trek.query.filter_by(status='Open')

    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))

    open_treks = query.all()
    my_bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('user/dashboard.html', treks=open_treks, bookings=my_bookings)

@user_bp.route('/book/<int:trek_id>')
@login_required
@user_required
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    # sirf open trek book ho sakta hai
    if trek.status != 'Open':
        print("Trek open nahi hai!")
        return redirect(url_for('user.dashboard'))

    # overbooking check
    if trek.available_slots <= 0:
        print("Slots full!")
        return redirect(url_for('user.dashboard'))

    # already booked check
    already_booked = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek_id,
        status='Booked'
    ).first()
    if already_booked:
        print("Already booked!")
        return redirect(url_for('user.dashboard'))

    # booking karo
    new_booking = Booking(
        user_id=current_user.id,
        trek_id=trek_id,
        status='Booked'
    )
    trek.available_slots -= 1
    db.session.add(new_booking)
    db.session.commit()
    print("Booked!")
    return redirect(url_for('user.bookings'))


# @user_bp.route('/bookings')
# @login_required
# @user_required
# def bookings():
#     my_bookings = Booking.query.filter_by(user_id=current_user.id).all()
#     return render_template('user/bookings.html', bookings=my_bookings)


# @user_bp.route('/cancel/<int:booking_id>')
# @login_required
# @user_required
# def cancel_booking(booking_id):
#     booking = Booking.query.get_or_404(booking_id)

#     # sirf apni booking cancel kar sakta hai
#     if booking.user_id != current_user.id:
#         return redirect(url_for('user.bookings'))

#     # slots wapas karo
#     trek = Trek.query.get(booking.trek_id)
#     trek.available_slots += 1

#     booking.status = 'Cancelled'
#     db.session.commit()
#     print("Cancelled!")
#     return redirect(url_for('user.bookings'))


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@user_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.phone = request.form.get('phone')
        db.session.commit()
        print("Profile updated!")
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html')

@user_bp.route('/bookings')
@login_required
@user_required
def bookings():
    my_bookings = Booking.query.filter_by(user_id=current_user.id).all()
    # har booking ke saath trek fetch karo
    booking_data = []
    for booking in my_bookings:
        trek = Trek.query.get(booking.trek_id)
        booking_data.append({
            'booking': booking,
            'trek': trek
        })
    return render_template('user/bookings.html', booking_data=booking_data)


@user_bp.route('/cancel/<int:booking_id>')
@login_required
@user_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != current_user.id:
        return redirect(url_for('user.bookings'))

    # trek exist karta hai toh hi slots wapas karo
    trek = Trek.query.get(booking.trek_id)
    if trek:
        trek.available_slots += 1

    booking.status = 'Cancelled'
    db.session.commit()
    print("Cancelled!")
    return redirect(url_for('user.bookings'))