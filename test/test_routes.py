import io
import pytest
from app import create_app, db
from app.models import Category, MenuItem

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_add_category(client, mocker):
    fake_restaurant = mocker.Mock()
    fake_restaurant.id = "fake-id-123"
    fake_restaurant.name = "Fake Resto"
    fake_restaurant.categories = []

    mocker.patch("flask_login.utils._get_user", return_value=fake_restaurant)

    fake_category = Category(category="Postres", restaurant_id=fake_restaurant.id)
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
    fake_restaurant.categories = []

    mocker.patch("flask_login.utils._get_user", return_value=fake_restaurant)
    mocker.patch("app.routes.upload_image_to_supabase",
                 return_value="http://fake-url.com/image.png")

    fake_category = Category(category="Entradas", restaurant_id=fake_restaurant.id)
    fake_category.id = "cat-123"

    fake_item = MenuItem(name="Pizza", category_id=fake_category.id,
                         image="http://fake-url.com/image.png")

    mocker.patch("app.models.Category.query.get", return_value=fake_category)
    mocker.patch("app.models.MenuItem.query.filter_by",
                 return_value=mocker.Mock(first=lambda: None))
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




