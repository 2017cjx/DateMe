from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect, CSRFError # ✅ CSRFProtect のみインポート
from flask_login import login_required, current_user
from wtforms.fields import HiddenField  # ✅ 追加
from wtforms import SelectField, SubmitField
from ..database import db
from ..models import Date_meal_options, Date_activity_options, Date_meeting_locations, Date_responses, Date_form

respond = Blueprint("respond", __name__, template_folder="../../templates")
csrf = CSRFProtect()  # ✅ CSRF を適用

class ResponseForm(FlaskForm):
    response_yes_no = SelectField("参加", choices = [("yes", "Yes"), ("no", "No")])
    submit = SubmitField("Next")

class SelectOptionsForm(FlaskForm):
    csrf_token = HiddenField()  # ✅ CSRF トークンを明示的に追加
    submit = SubmitField("Next")

@respond.errorhandler(CSRFError)
def handle_csrf_error(e):
    print("🚨 CSRF 検証失敗:", str(e))  # CSRF 失敗時にエラーをログに出す
    return "CSRF Token Error", 400

@respond.route("/<uuid:form_uuid>", methods=["GET", "POST"])
def respond_to_invite(form_uuid):
    form = ResponseForm()
    date_form = Date_form.query.filter_by(uuid=str(form_uuid)).first_or_404()

    if request.method == "POST" and form.validate_on_submit():
        response_value = form.response_yes_no.data
        response_yes_no = response_value == "yes"

        response = Date_responses.query.filter_by(form_id=date_form.id).first()

        if response:
            response.response_yes_no = response_yes_no
        else:
            response = Date_responses(form_id=date_form.id, response_yes_no=response_yes_no)
            db.session.add(response)
        
        db.session.commit()
    
        if response_value == "no":
            return render_template("respond_no_thank_you.html")
        
        return redirect(url_for("respond.respond_select_options", form_uuid=form_uuid))

    return render_template("respond_to_invite.html", form_uuid=form_uuid, form=form)

@respond.route("/select/<uuid:form_uuid>", methods=["GET", "POST"])
def respond_select_options(form_uuid):
    form = SelectOptionsForm()  # ✅ 修正: 適切なフォームを適用
    date_form = Date_form.query.filter_by(uuid=str(form_uuid)).first_or_404()
    meals = Date_meal_options.query.filter_by(form_id=date_form.id).all()
    activities = Date_activity_options.query.filter_by(form_id=date_form.id).all()
    meeting_locations = Date_meeting_locations.query.filter_by(form_id=date_form.id).all()

    response = Date_responses.query.filter_by(form_id=date_form.id).first()


    if form.validate_on_submit():
        print("✅ フォームバリデーション成功")
    else:
        print("❌ フォームバリデーション失敗", form.errors)

    if request.method == "POST":
        print("🚀 受け取ったフォームデータ:", request.form)


    if request.method == "POST" and form.validate_on_submit():
        selected_meals = request.form.getlist("meal_choices")
        selected_activities = request.form.getlist("activity_choices")
        selected_location = request.form.get("location_choices", default="0")

        if not selected_location or not selected_location.isdigit():
            flash("無効な選択肢です", "danger")
            return redirect(url_for("respond.respond_select_options", form_uuid=form_uuid))

        selected_location = int(selected_location)  # 🔥 ここで int に変換しておく

        if selected_location not in [loc.id for loc in meeting_locations]:
            flash("不正な選択肢です", "danger")
            return redirect(url_for("respond.respond_select_options", form_uuid=form_uuid))

        if any(m is None or int(m) not in [meal.id for meal in meals] for m in selected_meals):
            flash("不正な選択肢です", "danger")
            return redirect(url_for("respond.respond_select_options", form_uuid=form_uuid))

        if any(a is None or int(a) not in [activity.id for activity in activities] for a in selected_activities):
            flash("不正な選択肢です", "danger")
            return redirect(url_for("respond.respond_select_options", form_uuid=form_uuid))

        if len(selected_meals) > 2 or len(selected_activities) > 2:
            flash("選択肢は最大2つまでです", "danger")
            return redirect(url_for("respond.respond_select_options", form_uuid=form_uuid))


        if response:
            response.response_yes_no = True  # ✅ Yes をセット
            response.selected_meal_1 = int(selected_meals[0]) if selected_meals else None
            response.selected_meal_2 = int(selected_meals[1]) if len(selected_meals) > 1 else None
            response.selected_activity_1 = int(selected_activities[0]) if selected_activities else None
            response.selected_activity_2 = int(selected_activities[1]) if len(selected_activities) > 1 else None
            response.selected_location = int(selected_location) if selected_location else None

        else:
            new_response = Date_responses(
                form_id=date_form.id,
                response_yes_no = True,  # ✅ Yes をセット
                selected_meal_1=int(selected_meals[0]) if selected_meals else None,
                selected_meal_2=int(selected_meals[1]) if len(selected_meals) > 1 else None,
                selected_activity_1=int(selected_activities[0]) if selected_activities else None,
                selected_activity_2=int(selected_activities[1]) if len(selected_activities) > 1 else None,
                selected_location=int(selected_location) if selected_location else None
            )
            db.session.add(new_response)
        
        db.session.commit()

        print(f"✅ Saved response for form_id={date_form.id}")

        return redirect(url_for("respond.confirm_response", form_uuid=form_uuid))

    return render_template("respond_to_options.html", form_uuid=form_uuid, meals=meals, activities=activities, locations=meeting_locations, form=form)

@respond.route("/confirm/<uuid:form_uuid>", methods=["GET", "POST"])
def confirm_response(form_uuid):
    date_form = Date_form.query.filter_by(uuid=str(form_uuid)).first_or_404()

    # if date_form.creator_id != current_user.id:
    #     flash("アクセス権がありません", "danger")
    #     return redirect(url_for("main.dashboard"))

    response = Date_responses.query.filter_by(form_id=date_form.id).order_by(Date_responses.id.desc()).first()

    if not response:
        return "No response found", 404
    
    print(f"✅ Found response: {response.__dict__}")
    
    selected_meal_1 = Date_meal_options.query.get(response.selected_meal_1) if response.selected_meal_1 else None
    selected_meal_2 = Date_meal_options.query.get(response.selected_meal_2) if response.selected_meal_2 else None
    selected_activity_1 = Date_activity_options.query.get(response.selected_activity_1) if response.selected_activity_1 else None
    selected_activity_2 = Date_activity_options.query.get(response.selected_activity_2) if response.selected_activity_2 else None
    selected_location = Date_meeting_locations.query.get(response.selected_location) if response.selected_location else None
    
    return render_template(
        "respond_confirm.html",
        response=response,
        form_uuid=form_uuid,
        selected_meal_1=selected_meal_1,
        selected_meal_2=selected_meal_2,
        selected_activity_1=selected_activity_1,
        selected_activity_2=selected_activity_2,
        selected_location=selected_location
    )

@respond.route("/thank_you/<uuid:form_uuid>")
def respond_thank_you(form_uuid):
    return render_template("respond_thank_you.html", form_uuid=form_uuid)