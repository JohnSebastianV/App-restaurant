import sys
import os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    yield app

@pytest.fixture
def client(app):
    with app.app_context():
        with app.test_client() as client:
            yield client




