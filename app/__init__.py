from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate   # 👈 importa Flask-Migrate
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()  # 👈 inicializar

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "super-secret-key"

    USER = os.getenv("user")
    PASSWORD = os.getenv("password")
    HOST = os.getenv("host")
    PORT = os.getenv("port")
    DBNAME = os.getenv("dbname")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)   # 👈 registrar Flask-Migrate
    login_manager.login_view = "main.login"

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app


