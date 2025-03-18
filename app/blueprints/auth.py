from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from app.models import User
from app.database import db

auth = Blueprint("auth", __name__, template_folder="../../templates")

# リミットレート（1分間に5回まで）
limiter = Limiter(get_remote_address, default_limits=["30 per minute"])
csrf = CSRFProtect()

class SignupForm(FlaskForm):
    username = StringField("User name", validators=[DataRequired(), Length(min=3,max=50)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    username = StringField("User name", validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Login")

@auth.route("/signup", methods=['GET', 'POST'])
@limiter.limit("30 per minute")  # ✅ ルートごとに適用
def signup():

    form = SignupForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # すでに存在するユーザー名のチェック
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("このユーザー名はすでに使用されています", "danger")
            return redirect(url_for("auth.signup"))

        hashed_pass = generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)
        user = User(username=username, password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("auth.login"))

    return render_template("signup.html", form=form)

@auth.route("/login", methods=['GET', 'POST'])
@limiter.limit("30 per minute") #1分間に5回までログイン施行可能
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash("User not found", "danger")
            return redirect(url_for("auth.login"))


        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("admin.dashboard"))
        
        return render_template('login.html', msg='ユーザー名/パスワードが違います', form=form)

    return render_template('login.html', msg='', form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ログアウトしました", "success")
    return redirect(url_for("auth.login"))
