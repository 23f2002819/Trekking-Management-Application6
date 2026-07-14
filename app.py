import os
from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import User, Trek, Booking
from models import db

from routes.auth import auth_bp

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


db.init_app(app)

app.register_blueprint(auth_bp)

from routes.admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

from routes.staff import staff_bp
app.register_blueprint(staff_bp, url_prefix='/staff')

from routes.user import user_bp
app.register_blueprint(user_bp, url_prefix='/user')

from flask import redirect, url_for

@app.route('/')
def index():
    return redirect(url_for('auth.login'))
with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run(debug=True)
