import io
import pytest
from app import create_app, db
from app.models import Category, MenuItem, Restaurant


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_add_category(client, mocker):
    fake_restaurant = mocker.Mock()
    fake_restaurant.id = "fake-id-123"
    fake_restaurant.name = "Fake Resto"
    fake_restaurant.categories = []

    mocker.patch("flask_login.utils._get_user", return_value=fake_restaurant)

    mocker.patch("app.models.Category.query.filter_by",
                 return_value=mocker.Mock(first=lambda: None))
    mocker.patch("app.db.session.add")
    mocker.patch("app.db.session.commit")

    response = client.post("/add_category",
                           data={"category": "Postres"},
                           follow_redirects=True)

    assert response.status_code == 200
    assert "Categoría agregada correctamente." in response.data.decode("utf-8")


def test_add_item(client, mocker):
    fake_restaurant = mocker.Mock()
    fake_restaurant.id = "fake-id-123"
    fake_restaurant.name = "Fake Resto"

    mocker.patch("flask_login.utils._get_user", return_value=fake_restaurant)
    mocker.patch("app.routes.upload_image_to_supabase",
                 return_value="http://fake-url.com/image.png")

    fake_category = Category(category="Entradas", restaurant_id=fake_restaurant.id)
    fake_category.id = "cat-123"

    mocker.patch("app.models.Category.query.get", return_value=fake_category)
    mocker.patch("app.db.session.add")
    mocker.patch("app.db.session.commit")

    data = {
        "name": "Pizza",
        "price": "12.5",
        "description": "Muy rica",
        "image": (io.BytesIO(b"fake-image-data"), "pizza.png"),
    }

    response = client.post(f"/add_item/{fake_category.id}",
                           data=data,
                           content_type="multipart/form-data",
                           follow_redirects=True)

    assert response.status_code == 200
    assert "Plato agregado con éxito" in response.data.decode("utf-8")


def test_login_invalid_credentials(client, mocker):
    # Simular restaurante existente
    fake_restaurant = Restaurant(name="RestFail", schedule="9-5",
                                 location="TestCity", description="test", image="url")
    fake_restaurant.set_password("Password123")

    mocker.patch("app.models.Restaurant.query.filter_by",
                 return_value=mocker.Mock(first=lambda: fake_restaurant))
    mocker.patch.object(fake_restaurant, "check_password", return_value=False)

    response = client.post("/login",
                           data={"name": "RestFail", "password": "wrong"},
                           follow_redirects=True)

    assert response.status_code == 200
    assert "incorrectos" in response.data.decode("utf-8")


def test_register_restaurant(client, mocker):
    mocker.patch("app.routes.upload_image_to_supabase",
                 return_value="http://fake.url/image.png")

    mocker.patch("app.models.Restaurant.query.filter_by",
                 return_value=mocker.Mock(first=lambda: None))
    mocker.patch("app.db.session.add")
    mocker.patch("app.db.session.commit")

    data = {
        "name": "NuevoRest",
        "password": "Password123",
        "schedule": "8-4",
        "location": "Bogotá",
        "description": "Un restaurante nuevo",
        "image": (io.BytesIO(b"fake-image-data"), "resto.png"),
    }
    response = client.post("/register",
                           data=data,
                           content_type="multipart/form-data",
                           follow_redirects=True)

    assert response.status_code == 200
    assert "Restaurante registrado con éxito" in response.data.decode("utf-8")




