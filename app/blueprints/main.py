from flask import Blueprint, render_template

main = Blueprint("main", __name__, template_folder="../../templates")

@main.route("/")
def home():
    return render_template('home.html')

@main.route("/terms")
def terms():
    return render_template("terms.html")

@main.route("/privacy")
def privacy():
    return render_template("privacy.html")