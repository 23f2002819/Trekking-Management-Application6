from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
db = SQLAlchemy()

class User(db.Model,UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable = False)
    email = db.Column(db.String(100),nullable = False, unique=True)
    password = db.Column(db.String(100),nullable = False)
    role = db.Column(db.String(20),nullable = False)
    status = db.Column(db.String(20),nullable = False, default='active')
    phone = db.Column(db.String(20),nullable = True)
    # created_at = db.Column(db.DateTime, default=datetime.utcnow)/
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Trek(db.Model):
    __tablename__="treks"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),nullable = False)
    location = db.Column(db.String(20),nullable = False)
    difficulty = db.Column(db.String(20),nullable=False)
    duration = db.Column(db.Integer,nullable=False)
    total_slots = db.Column(db.Integer,nullable=False)
    available_slots = db.Column(db.Integer,nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20),nullable=False,default='pending')
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=True)

class Booking(db.Model):
    __tablename__="bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    trek_id = db.Column(db.Integer,db.ForeignKey('treks.id'),nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20),nullable=False,default='Booked')
 