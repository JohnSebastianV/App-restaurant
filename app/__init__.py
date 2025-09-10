import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    load_dotenv()

    app = Flask(__name__,
                static_folder="app/static",
                template_folder="app/templates")

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_key")

    USER = os.getenv("user")
    PASSWORD = os.getenv("password")
    HOST = os.getenv("host")
    PORT = os.getenv("port")
    DBNAME = os.getenv("dbname")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    )

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message_category = "info"

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
