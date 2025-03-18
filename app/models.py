from app.database import db
from flask_login import UserMixin
from datetime import datetime
import pytz
import uuid

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

class Date_form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=True, default=lambda: str(uuid.uuid4()))
    creator_id = db.Column(db.Integer)
    partner_name = db.Column(db.String(100), nullable=False)
    tokyo_timezone = pytz.timezone('Asia/Tokyo')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(tokyo_timezone))

class Date_meal_options(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey("date_form.id"), nullable=False)
    meal_title = db.Column(db.String(50),nullable=False)
    meal_image = db.Column(db.String(100),nullable=True)

class Date_activity_options(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey("date_form.id"), nullable=False)
    activity_title = db.Column(db.String(50),nullable=False)
    activity_image = db.Column(db.String(100),nullable=True)

class Date_meeting_locations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey("date_form.id"), nullable=False)
    location_title = db.Column(db.String(50),nullable=False)

class Date_responses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey("date_form.id"), nullable=False)
    response_yes_no = db.Column(db.Boolean)
    selected_meal_1 = db.Column(db.Integer)
    selected_meal_2 = db.Column(db.Integer)
    selected_activity_1 = db.Column(db.Integer)
    selected_activity_2 = db.Column(db.Integer)
    selected_location = db.Column(db.Integer)

__all__ = ["User","Date_form","Date_meal_options","Date_activity_options","Date_meeting_locations","Date_responses"]
