from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from ..database import db
from ..models import Date_form, Date_meal_options, Date_activity_options, Date_meeting_locations
import os
from config import DEFAULT_MEALS, DEFAULT_ACTIVITIES, DEFAULT_MEETING_LOCATIONS
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, FileField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired

create = Blueprint("create", __name__, template_folder="../../templates")
csrf = CSRFProtect()
limiter = Limiter(get_remote_address, default_limits=["30 per minute"])

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

class CreateDateForm(FlaskForm):
    partner_name = StringField("パートナーの名前", validators=[DataRequired()])
    submit = SubmitField("作成")

class MealForm(FlaskForm):
    meal_title = StringField("食事のタイトル", validators=[DataRequired()])
    meal_image = FileField("画像")
    submit = SubmitField("Add")

class ActivityForm(FlaskForm):
    activity_title = StringField("アクティビティのタイトル", validators=[DataRequired()])
    activity_image = FileField("画像")
    submit = SubmitField("Add")

class LocationForm(FlaskForm):
    location_title = StringField("待ち合わせ場所のタイトル", validators=[DataRequired()])
    submit = SubmitField("Add")

@create.route("/", methods=["GET", "POST"])
@login_required
@limiter.limit("30 per minute")
def create_date_form():
    form = CreateDateForm()

    if request.method == "POST" and form.validate_on_submit():
        partner_name = form.partner_name.data

        if not partner_name or len(partner_name) > 100:
            flash("入力が無効です", "danger")
            return redirect(url_for("create.create_date_form"))

        new_form = Date_form(creator_id=current_user.id, partner_name=partner_name)
        db.session.add(new_form)
        db.session.commit()

        add_default_meals(new_form.id)
        add_default_activities(new_form.id)
        add_default_locations(new_form.id)

        session["form_id"] = new_form.id
        return redirect(url_for("create.add_meals", form_id=new_form.id))

    return render_template("create_date.html", form=form)

def add_default_meals(form_id):
    existing_meals = Date_meal_options.query.filter_by(form_id=form_id).count()
    if existing_meals == 0:
        for meal in DEFAULT_MEALS:
            new_meal = Date_meal_options(form_id=form_id, meal_title=meal["meal_title"], meal_image=meal["meal_image"])
            db.session.add(new_meal)
        db.session.commit()

@create.route("/add_meals/<int:form_id>", methods=["GET", "POST"])
@login_required
@limiter.limit("30 per minute")
def add_meals(form_id):
    form = MealForm()
    meals = Date_meal_options.query.filter_by(form_id=form_id).all()

    date_form = Date_form.query.get_or_404(form_id)

    if date_form.creator_id != current_user.id:
        flash("不正なアクセスです。", "danger")
        return redirect(url_for("main.dashboard"))

    if form.validate_on_submit():

        meal_title = form.meal_title.data.strip() if form.meal_title.data else None
        meal_image = form.meal_image.data

        if not meal_title:
            flash("食事のタイトルを入力してください", "danger")
            return redirect(url_for("create.add_meals", form_id=form_id))

        image_path = None

        if meal_image and allowed_file(meal_image.filename):
            filename = secure_filename(meal_image.filename)
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            meal_image.save(save_path)
            image_path = f"img/{filename}"

        new_meal = Date_meal_options(form_id=form_id, meal_title=meal_title, meal_image=image_path)
        db.session.add(new_meal)
        db.session.commit()

        return redirect(url_for("create.add_meals", form_id=form_id))

    return render_template("add_meals.html", form_id=form_id, meals=meals, form=form)

def add_default_activities(form_id):
    existing_activities = Date_activity_options.query.filter_by(form_id=form_id).count()
    if existing_activities == 0:
        for activity in DEFAULT_ACTIVITIES:
            new_activity = Date_activity_options(
                form_id=form_id,
                activity_title=activity["activity_title"],
                activity_image=activity["activity_image"]
            )
            db.session.add(new_activity)
        db.session.commit()

@create.route("/add_activities/<int:form_id>", methods=['GET','POST'])
@login_required
@limiter.limit("30 per minute")
def add_activities(form_id):
    form = ActivityForm()
    activities = Date_activity_options.query.filter_by(form_id=form_id).all()

    date_form = Date_form.query.get_or_404(form_id)

    if date_form.creator_id != current_user.id:
        flash("不正なアクセスです。", "danger")
        return redirect(url_for("main.dashboard"))

    if form.validate_on_submit():
        activity_title = form.activity_title.data
        activity_image = form.activity_image.data

        image_path = None
        if activity_image and allowed_file(activity_image.filename):
            filename = activity_image.filename
            save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            activity_image.save(save_path)
            image_path = f"img/{filename}"

        new_activity = Date_activity_options(form_id=form_id, activity_title=activity_title, activity_image=image_path)
        db.session.add(new_activity)
        db.session.commit()
        
        return redirect(url_for("create.add_activities", form_id=form_id))  
    
    return render_template("add_activities.html", form_id=form_id, activities=activities, form=form)

def add_default_locations(form_id):
    existing_locations = Date_meeting_locations.query.filter_by(form_id=form_id).count()
    if existing_locations == 0:
        for location in DEFAULT_MEETING_LOCATIONS:
            new_location = Date_meeting_locations(
                form_id=form_id,
                location_title=location["location_title"],
            )
            db.session.add(new_location)
        db.session.commit()

@create.route("/add_meeting_locations/<int:form_id>", methods=['GET','POST'])
@login_required
@limiter.limit("30 per minute")
def add_meeting_locations(form_id):
    form = LocationForm()
    meeting_locations = Date_meeting_locations.query.filter_by(form_id=form_id).all()

    date_form = Date_form.query.get_or_404(form_id)

    if date_form.creator_id != current_user.id:
        flash("不正なアクセスです。", "danger")
        return redirect(url_for("main.dashboard"))
    
    if form.validate_on_submit():
        location_title = form.location_title.data
        new_location = Date_meeting_locations(form_id=form_id, location_title=location_title)
        db.session.add(new_location)
        db.session.commit()
        return redirect(url_for("create.add_meeting_locations", form_id=form_id))
    
    return render_template("add_meeting_locations.html", form_id=form_id, meeting_locations=meeting_locations, form=form)

@create.route("/add_date_confirmation/<int:form_id>", methods=['GET','POST'])
@login_required
@limiter.limit("30 per minute")
def add_date_confirmation(form_id):
    meals = Date_meal_options.query.filter_by(form_id=form_id).all()
    activities = Date_activity_options.query.filter_by(form_id=form_id).all()
    meeting_locations = Date_meeting_locations.query.filter_by(form_id=form_id).all()
    
    return render_template("add_date_confirmation.html", form_id=form_id, meals=meals, activities=activities, meeting_locations=meeting_locations)