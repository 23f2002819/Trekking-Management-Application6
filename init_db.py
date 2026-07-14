from werkzeug.security import generate_password_hash
from app import app
from models import db, User

def by_default_admin():
    with app.app_context():
        existing_admin = User.query.filter_by(role='admin').first()
        if not existing_admin:
            admin_user = User(
                name='Soumyodip',
                email='sbsb96745@gmail.com',
                password=generate_password_hash('sb321'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit() 

by_default_admin()