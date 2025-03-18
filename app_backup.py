from flask import Flask, render_template, request, session, redirect, url_for
from flask_login import LoginManager
from config import Config, DEFAULT_MEALS, DEFAULT_ACTIVITIES, DEFAULT_MEETING_LOCATIONS
from app.database import db, migrate
from app.blueprints.auth import auth
from app.models import *
import os

app = Flask(__name__)
app.config.from_object(Config)

# DB & Migrate 初期化
db.init_app(app)
migrate.init_app(app, db)

# Flask-Login 設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprint 登録
app.register_blueprint(auth, url_prefix="/")

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/admin")
def dashboard():
    return render_template('admin.html')

@app.route("/admin/create", methods=['GET','POST'])
def create_date_form():
    if request.method =="POST":
        partner_name = request.form.get("partner_name")
        new_form = Date_form(creator_id=1, partner_name=partner_name)
        db.session.add(new_form)
        db.session.commit()

        session["form_id"] = new_form.id
        return redirect(url_for("add_meals", form_id=new_form.id))
    
    return render_template("create_date.html")

def add_default_meals(form_id):
    existing_meals = Date_meal_options.query.filter_by(form_id=form_id).count()
    if existing_meals == 0:
        for meal in DEFAULT_MEALS:
            new_meal = Date_meal_options(
                form_id=form_id,
                meal_title=meal["meal_title"],
                meal_image=meal["meal_image"]
            )
            db.session.add(new_meal)
        db.session.commit()

@app.route("/admin/add_meals/<int:form_id>", methods=['GET','POST'])
def add_meals(form_id):
    add_default_meals(form_id)

    meals = Date_meal_options.query.filter_by(form_id=form_id).all()

    if request.method =="POST":
        meal_title = request.form.get("meal_title")
        meal_image = request.files.get("meal_image")

        if meal_image and meal_image.filename != "":
            filename = meal_image.filename
            save_path = os.path.join(app.static_folder,'img',filename)
            meal_image.save(save_path)
            image_path = f"img/{filename}"
        else:
            image_path=None
        
        new_meal = Date_meal_options(form_id=form_id, meal_title=meal_title, meal_image=image_path)
        db.session.add(new_meal)
        db.session.commit()

        return redirect(url_for("add_meals", form_id=form_id))
    
    return render_template("add_meals.html", form_id=form_id, meals=meals)

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

@app.route("/admin/add_activities/<int:form_id>", methods=['GET','POST'])
def add_activities(form_id):
    add_default_activities(form_id)
    activities = Date_activity_options.query.filter_by(form_id=form_id).all()

    if request.method =="POST":
        activity_title = request.form.get("activity_title")
        activity_image = request.files.get("activity_image")

        if activity_image and activity_image.filename != "":
            filename = activity_image.filename
            save_path = os.path.join(app.static_folder, 'img', filename)
            activity_image.save(save_path)
            image_path = f"img/{filename}"
        else:
            image_path=None

        new_activity = Date_activity_options(form_id=form_id, activity_title=activity_title, activity_image=image_path)
        db.session.add(new_activity)
        db.session.commit()

        return redirect(url_for("add_activities", form_id=form_id))  
    
    return render_template("add_activities.html", form_id=form_id, activities=activities)

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

@app.route("/admin/add_meeting_locations/<int:form_id>", methods=['GET','POST'])
def add_meeting_locations(form_id):
    add_default_locations(form_id)
    meeting_locations = Date_meeting_locations.query.filter_by(form_id=form_id).all()

    if request.method =="POST":
        location_title = request.form.get("location_title")
        new_location = Date_meeting_locations(form_id=form_id, location_title=location_title)
        db.session.add(new_location)
        db.session.commit()
        return redirect(url_for("add_meeting_locations", form_id=form_id))
    
    return render_template("add_meeting_locations.html", form_id=form_id, meeting_locations=meeting_locations)

@app.route("/admin/add_date_confirmation/<int:form_id>", methods=['GET','POST'])
def add_date_confirmation(form_id):
    meals = Date_meal_options.query.filter_by(form_id=form_id).all()
    activities = Date_activity_options.query.filter_by(form_id=form_id).all()
    meeting_locations = Date_meeting_locations.query.filter_by(form_id=form_id).all()
    
    return render_template("add_date_confirmation.html", form_id=form_id, meals=meals, activities=activities, meeting_locations=meeting_locations)

# 回答者向けページ

@app.route("/admin/generate_link/<int:form_id>")
def generate_link(form_id):
    link = f"{request.host_url}respond/{form_id}"
    return render_template("generate_respond_link.html", link=link, form_id=form_id)

@app.route("/respond/<int:form_id>", methods=['GET', 'POST'])
def respond_to_invite(form_id):
    if request.method == "POST":
        response = request.form.get("response_yes_no")
        if response == "no":
            return render_template("respond_thank_you.html")
        return redirect(url_for("respond_select_options", form_id=form_id))
    return render_template("respond_to_invite.html")

@app.route("/respond/<int:form_id>/select", methods=["GET", "POST"])
def respond_select_options(form_id):
    meals = Date_meal_options.query.filter_by(form_id=form_id).all()
    activities = Date_activity_options.query.filter_by(form_id=form_id).all()
    meeting_locations = Date_meeting_locations.query.filter_by(form_id=form_id).all()

    selected_meals = []
    selected_activities = []
    selected_location = None

    if request.method == "POST":
        selected_meals = request.form.getlist("meal_choices")
        selected_activities = request.form.getlist("activity_choices")
        selected_location = request.form.get("location_choices")
    
        selected_meal_1 = int(selected_meals[0]) if len(selected_meals) > 0 else None
        selected_meal_2 = int(selected_meals[1]) if len(selected_meals) > 1 else None
        selected_activity_1 = int(selected_activities[0]) if len(selected_activities) > 0 else None
        selected_activity_2 = int(selected_activities[1]) if len(selected_activities) > 1 else None
        selected_location = int(selected_location) if selected_location else None

        new_response = Date_responses(
            form_id=form_id,
            selected_meal_1=selected_meal_1,
            selected_meal_2=selected_meal_2,
            selected_activity_1=selected_activity_1,
            selected_activity_2=selected_activity_2,
            selected_location=selected_location
        )
        db.session.add(new_response)
        db.session.commit()

        return redirect(url_for("confirm_response", form_id=form_id))

    return render_template("respond_to_options.html", form_id=form_id, meals=meals, activities=activities, locations=meeting_locations)

@app.route("/respond/<int:form_id>/confirm", methods=["GET", "POST"])
def confirm_response(form_id):
    response = Date_responses.query.filter_by(form_id=form_id).order_by(Date_responses.id.desc()).first()

    if not response:
        return "No response found", 404
    
    selected_meal_1 = Date_meal_options.query.get(response.selected_meal_1) if response.selected_meal_1 else None
    selected_meal_2 = Date_meal_options.query.get(response.selected_meal_2) if response.selected_meal_2 else None
    selected_activity_1 = Date_activity_options.query.get(response.selected_activity_1) if response.selected_activity_1 else None
    selected_activity_2 = Date_activity_options.query.get(response.selected_activity_2) if response.selected_activity_2 else None
    selected_location = Date_meeting_locations.query.get(response.selected_location) if response.selected_location else None
    
    return render_template(
        "respond_confirm.html",
        response=response,
        form_id=form_id,
        selected_meal_1=selected_meal_1,
        selected_meal_2=selected_meal_2,
        selected_activity_1=selected_activity_1,
        selected_activity_2=selected_activity_2,
        selected_location=selected_location
    )

@app.route("/respond/<int:form_id>/thank_you")
def respond_thank_you(form_id):
    return render_template("respond_thank_you.html", form_id=form_id)

if __name__ == "__main__":
    app.run(debug=True)