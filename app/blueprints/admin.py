from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_login import login_required, current_user
from ..database import db
from ..models import Date_form, Date_meal_options, Date_activity_options, Date_meeting_locations, Date_responses
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from config import DEFAULT_MEALS, DEFAULT_ACTIVITIES, DEFAULT_MEETING_LOCATIONS

admin = Blueprint("admin", __name__, template_folder="../../templates")

limiter = Limiter(get_remote_address, default_limits=["30 per minute"])

@admin.route("/")
@login_required
@limiter.limit("30 per minute")
def dashboard():

    date_forms = Date_form.query.filter_by(creator_id=current_user.id).order_by(Date_form.created_at.desc()).all()

    date_data = []
    for index, form in enumerate(date_forms, start=1):
        response = Date_responses.query.filter_by(form_id=form.id).first()

        if response:
            response_status = "Yes" if response.response_yes_no else "No Thanks"
        else:
            response_status = "No Response Yet"
        
        response_details = None
        if response_status == "Yes":
            selected_meal_1 = Date_meal_options.query.get(response.selected_meal_1)
            selected_meal_2 = Date_meal_options.query.get(response.selected_meal_2)
            selected_activity_1 = Date_activity_options.query.get(response.selected_activity_1)
            selected_activity_2 = Date_activity_options.query.get(response.selected_activity_2)
            selected_location = Date_meeting_locations.query.get(response.selected_location)

            response_details = {
                "meal_1" : selected_meal_1.meal_title if selected_meal_1 else "-",
                "meal_2" : selected_meal_2.meal_title if selected_meal_2 else "-",
                "activity_1" : selected_activity_1.activity_title if selected_activity_1 else "-",
                "activity_2" : selected_activity_2.activity_title if selected_activity_2 else "-",
                "location" : selected_location.location_title if selected_location else "-"
            }
        
        response_url = None
        if response_status == "No Response Yet":
            response_url = url_for("respond.respond_to_invite", form_uuid=form.uuid, _external=True)
        
        date_data.append({
            "number": index,
            "id": form.id,
            "partner_name": form.partner_name,
            "response_status": response_status,
            "response_details": response_details,
            "response_url": response_url
        })

    return render_template('admin.html', date_data=date_data)

@admin.route("delete/<int:form_id>", methods=["POST"])
@login_required
@limiter.limit("30 per minute")
def delete_date(form_id):
    form = Date_form.query.get_or_404(form_id)

    Date_meal_options.query.filter_by(form_id=form_id).delete()
    Date_activity_options.query.filter_by(form_id=form_id).delete()
    Date_meeting_locations.query.filter_by(form_id=form_id).delete()
    Date_responses.query.filter_by(form_id=form_id).delete()

    db.session.delete(form)
    db.session.commit()

    return redirect(url_for("admin.dashboard"))

@admin.route("/edit/<int:form_id>", methods=["GET","POST"])
@login_required
@limiter.limit("30 per minute")
def edit_date(form_id):
    form = Date_form.query.get_or_404(form_id)

    if request.method=="POST":
        form.partner_name = request.form.get("partner_name")
        db.session.commit()
        return redirect(url_for("admin.dashboard"))
    
    return render_template("edit_date.html", form=form)