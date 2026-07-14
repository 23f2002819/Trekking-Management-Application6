from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password  = request.form.get('password')
        role = request.form.get('role')

        is_user_exists = User.query.filter_by(email=email).first()
        if is_user_exists:
            print("exits")
            return redirect(url_for('auth.register'))
        new_User = User(
            name = name,
            email = email,
            password = generate_password_hash(password),
            role = role,
            status = "active" if role=='user' else 'pending'
        )
        db.session.add(new_User)
        db.session.commit()

        print("done")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        email=request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            if user.status == 'blacklisted':
                print("User blacklisted!")
                return redirect(url_for('auth.login'))
            login_user(user)
            print("login!")

            if(user.role=="admin"):
                return redirect(url_for('admin.dashboard'))
            elif(user.role=="staff"):
                return redirect(url_for('staff.dashboard'))
            
            else:
                return redirect(url_for('user.dashboard'))

        else:
            return redirect(url_for('auth.login'))
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    print("logged out")
    return redirect(url_for('auth.login'))