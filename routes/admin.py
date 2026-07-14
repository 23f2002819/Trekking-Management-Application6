from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, Trek, Booking
from functools import wraps
from datetime import datetime
admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='user').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()

    return render_template('admin/dashboard.html',
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings
    )

@admin_bp.route('/treks')
@login_required
@admin_required
def treks():
    all_treks = Trek.query.all()
    all_staff = User.query.filter_by(role='staff', status='active').all()
    return render_template('admin/treks.html', treks=all_treks, staff=all_staff)


@admin_bp.route('/treks/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_trek():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = int(request.form.get('duration'))
        total_slots = int(request.form.get('total_slots'))
        # start_date = request.form.get('start_date')
        # end_date = request.form.get('end_date')

        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        description = request.form.get('description')

        new_trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            total_slots=total_slots,
            available_slots=total_slots,
            start_date=start_date,
            end_date=end_date,
            description=description,
            status='Pending'
        )
        db.session.add(new_trek)
        db.session.commit()
        print("Trek created!")
        return redirect(url_for('admin.treks'))

    return render_template('admin/create_trek.html')


@admin_bp.route('/treks/edit/<int:trek_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if request.method == 'POST':
        trek.name = request.form.get('name')
        trek.location = request.form.get('location')
        trek.difficulty = request.form.get('difficulty')
        trek.duration = int(request.form.get('duration'))
        trek.total_slots = int(request.form.get('total_slots'))
        trek.status = request.form.get('status')
        db.session.commit()
        return redirect(url_for('admin.treks'))
    return render_template('admin/edit_trek.html', trek=trek)


@admin_bp.route('/treks/delete/<int:trek_id>')
@login_required
@admin_required
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    return redirect(url_for('admin.treks'))


@admin_bp.route('/staff')
@login_required
@admin_required
def staff():
    all_staff = User.query.filter_by(role='staff').all()
    all_treks = Trek.query.all()
    return render_template('admin/staff.html', staff=all_staff, treks=all_treks)


@admin_bp.route('/staff/approve/<int:user_id>')
@login_required
@admin_required
def approve_staff(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'active'
    db.session.commit()
    return redirect(url_for('admin.staff'))


@admin_bp.route('/staff/reject/<int:user_id>')
@login_required
@admin_required
def reject_staff(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'blacklisted'
    db.session.commit()
    return redirect(url_for('admin.staff'))


@admin_bp.route('/staff/assign/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def assign_trek(user_id):
    trek_id = int(request.form.get('trek_id'))
    trek = Trek.query.get_or_404(trek_id)
    trek.staff_id = user_id
    db.session.commit()
    print("Trek assigned!")
    return redirect(url_for('admin.staff'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.filter_by(role='user').all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/blacklist/<int:user_id>')
@login_required
@admin_required
def blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'blacklisted'
    db.session.commit()
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/unblock/<int:user_id>')
@login_required
@admin_required
def unblock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'active'
    db.session.commit()
    return redirect(url_for('admin.users'))

@admin_bp.route('/bookings')
@login_required
@admin_required
def bookings():
    all_bookings = Booking.query.all()
    booking_data = []
    for booking in all_bookings:
        user = User.query.get(booking.user_id)
        trek = Trek.query.get(booking.trek_id)
        booking_data.append({
            'booking': booking,
            'user': user,
            'trek': trek
        })
    return render_template('admin/bookings.html', booking_data=booking_data)


@admin_bp.route('/search')
@login_required
@admin_required
def search():
    query = request.args.get('q', '')
    
    treks = Trek.query.filter(Trek.name.ilike(f'%{query}%')).all()
    users = User.query.filter(
        User.role == 'user',
        User.name.ilike(f'%{query}%')
    ).all()
    staff = User.query.filter(
        User.role == 'staff',
        User.name.ilike(f'%{query}%')
    ).all()
    
    return render_template('admin/search.html', 
        query=query, treks=treks, users=users, staff=staff)

@admin_bp.route('/treks/approve/<int:trek_id>')
@login_required
@admin_required
def approve_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    trek.status = 'Approved'
    db.session.commit()
    return redirect(url_for('admin.treks'))