import sys
import os
import pytest

# Añadir carpeta raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    # Otros settings si quieres, por ejemplo:
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    yield app

@pytest.fixture
def client(app):
    # Activar contexto de aplicación
    with app.app_context():
        with app.test_client() as client:
            yield client




