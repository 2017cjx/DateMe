from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from .database import db, migrate
from .models import User
from .blueprints.admin import admin
from .blueprints.create import create
from .blueprints.respond import respond
from .blueprints.auth import auth
from .blueprints.main import main
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

csrf = CSRFProtect()

limiter = Limiter(get_remote_address, default_limits=["30 per minute"])

login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder='static')
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    limiter.init_app(app)

    # DB & Migrate 初期化
    db.init_app(app)
    migrate.init_app(app, db)

    # csrf保護を適用
    csrf.init_app(app)

    # Flask-Login 設定
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprint の登録
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(create, url_prefix="/create")
    app.register_blueprint(respond, url_prefix="/respond")

    return app

app = create_app()
