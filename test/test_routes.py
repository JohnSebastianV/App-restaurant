import io
import pytest
from app import create_app, db
from app.models import Category, MenuItem, Restaurant
from app.forms import RegisterForm, LoginForm


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        with app.app_context():
            yield client


# -----------------------
# Categorías
# -----------------------

def test_add_category(client, mocker):
    fake_restaurant = mocker.Mock()
    fake_restaurant.id = "fake-id-123"
    mocker.patch("flask_login.utils._get_user", return_value=fake_restaurant)

    mocker.patch("app.db.session.add")
    mocker.patch("app.db.session.commit")

    response = client.post("/add_category",
                           data={"category": "Postres"},
                           follow_redirects=True)
    assert response.status_code == 200
    assert "Categoría agregada correctamente" in response.data.decode("utf-8")


def test_edit_category(client, mocker):
    fake_restaurant = mocker.Mock()
    fake_restaurant.id = "rest-123"

    fake_category = Category(category="Bebidas", restaurant_id=fake_restaurant.id)
    fake_category.id = "cat-001"

    mocker.patch("flask_login.utils._get_user", return_value=fake_restaurant)
    mocker.patch("app.models.Category.query.get_or_404", return_value=fake_category)
    mocker.patch("app.db.session.commit")

    response = client.post(f"/edit_category/{fake_category.id}",
                           data={"category": "Cócteles"},
                           follow_redirects=True)
    assert "Categoría actualizada" in response.data.decode("utf-8")


def test_edit_category_no_permission(client, mocker):
    fake_restaurant = mocker.Mock()
    fake_restaurant.id = "rest-123"

    fake_category = Category(category="Postres", restaurant_id="otro-resto")
    fake_category.id = "cat-002"

    mocker.patch("flask_login.utils._get_user", return_value=fake_restaurant)
    mocker.patch("app.models.Category.query.get_or_404", return_value=fake_category)

    response = client.post(f"/edit_category/{fake_category.id}",
                           data={"category": "Tortas"},
                           follow_redirects=True)
    assert "No tienes permiso" in response.data.decode("utf-8")


def test_delete_category(client, mocker):
    fake_restaurant = mocker.Mock()
    fake_restaurant.id = "rest-123"

    fake_category = Category(category="Pastas", restaurant_id=fake_restaurant.id)
    fake_category.id = "cat-003"

    mocker.patch("flask_login.utils._get_user", return_value=fake_restaurant)
    mocker.patch("app.models.Category.query.get_or_404", return_value=fake_category)
    mocker.patch("app.db.session.delete")
    mocker.patch("app.db.session.commit")

    response = client.post(f"/delete_category/{fake_category.id}",
                           follow_redirects=True)
    assert "Categoría eliminada" in response.data.decode("utf-8")


# -----------------------
# Ítems
# -----------------------

def test_add_item(client, mocker):
    fake_restaurant = mocker.Mock()
    fake_restaurant.id = "fake-id-123"

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
    assert "Plato agregado con éxito" in response.data.decode("utf-8")


def test_edit_item_no_permission(client, mocker):
    fake_restaurant = mocker.Mock()
    fake_restaurant.id = "rest-123"

    fake_category = Category(category="Carnes", restaurant_id="otro-resto")
    fake_item = MenuItem(name="Filete", price=20, description="desc")
    fake_item.id = "item-123"
    fake_item.category = fake_category

    mocker.patch("flask_login.utils._get_user", return_value=fake_restaurant)
    mocker.patch("app.models.MenuItem.query.get_or_404", return_value=fake_item)

    response = client.post(f"/edit_item/{fake_item.id}",
                           data={"name": "Filete Angus"},
                           follow_redirects=True)
    assert "No tienes permiso" in response.data.decode("utf-8")


# -----------------------
# Autenticación
# -----------------------

def test_login_invalid_credentials(client, mocker):
    fake_restaurant = Restaurant(name="RestFail", schedule="9-5",
                                 location="TestCity", description="test", image="url")
    fake_restaurant.set_password("Password123")

    mocker.patch("app.models.Restaurant.query.filter_by",
                 return_value=mocker.Mock(first=lambda: fake_restaurant))
    mocker.patch.object(fake_restaurant, "check_password", return_value=False)

    response = client.post("/login",
                           data={"name": "RestFail", "password": "wrong"},
                           follow_redirects=True)
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
    assert "Restaurante registrado con éxito" in response.data.decode("utf-8")


def test_register_missing_fields(client):
    data = {
        "name": "",
        "password": "",
        "schedule": "",
        "location": "",
        "description": "",
    }
    response = client.post("/register", data=data, follow_redirects=True)
    assert "Todos los campos son obligatorios" in response.data.decode("utf-8")


def test_register_invalid_password(client, mocker):
    mocker.patch("app.models.Restaurant.query.filter_by",
                 return_value=mocker.Mock(first=lambda: None))
    data = {
        "name": "WeakRest",
        "password": "weak",
        "schedule": "8-4",
        "location": "Cali",
        "description": "Desc",
        "image": (io.BytesIO(b"fake"), "weak.png"),
    }
    response = client.post("/register",
                           data=data,
                           content_type="multipart/form-data",
                           follow_redirects=True)
    assert "La contraseña debe tener" in response.data.decode("utf-8")


def test_logout(client, mocker):
    fake_restaurant = mocker.Mock()
    fake_restaurant.id = "rest-123"
    mocker.patch("flask_login.utils._get_user", return_value=fake_restaurant)

    response = client.get("/logout", follow_redirects=True)
    assert "Sesión cerrada" in response.data.decode("utf-8")

# -----------------------
# Extra - Cobertura
# -----------------------

def test_register_duplicate_restaurant(client, mocker):
    """Registro falla si el nombre ya existe"""
    fake_restaurant = Restaurant(name="Duplicado", schedule="9-5",
                                 location="City", description="desc", image="url")
    mocker.patch("app.models.Restaurant.query.filter_by",
                 return_value=mocker.Mock(first=lambda: fake_restaurant))

    data = {
        "name": "Duplicado",
        "password": "Password123",
        "schedule": "9-5",
        "location": "Medellín",
        "description": "resto",
        "image": (io.BytesIO(b"fake-img"), "dup.png"),
    }
    response = client.post("/register",
                           data=data,
                           content_type="multipart/form-data",
                           follow_redirects=True)
    assert "ya está registrado" in response.data.decode("utf-8")


def test_delete_category_no_permission(client, mocker):
    """Intentar borrar una categoría de otro restaurante"""
    fake_restaurant = mocker.Mock()
    fake_restaurant.id = "rest-123"

    fake_category = Category(category="Ajeno", restaurant_id="otro-resto")
    fake_category.id = "cat-x"

    mocker.patch("flask_login.utils._get_user", return_value=fake_restaurant)
    mocker.patch("app.models.Category.query.get_or_404", return_value=fake_category)

    response = client.post(f"/delete_category/{fake_category.id}",
                           follow_redirects=True)
    assert "No tienes permiso" in response.data.decode("utf-8")


def test_login_nonexistent_user(client, mocker):
    """Login con usuario inexistente"""
    mocker.patch("app.models.Restaurant.query.filter_by",
                 return_value=mocker.Mock(first=lambda: None))

    response = client.post("/login",
                           data={"name": "NoExiste", "password": "1234"},
                           follow_redirects=True)
    assert "incorrectos" in response.data.decode("utf-8")


def test_add_item_invalid_category(client, mocker):
    """No se puede agregar un plato si la categoría no existe"""
    fake_restaurant = mocker.Mock()
    fake_restaurant.id = "rest-123"
    mocker.patch("flask_login.utils._get_user", return_value=fake_restaurant)

    mocker.patch("app.models.Category.query.get", return_value=None)

    data = {
        "name": "SinCat",
        "price": "10.0",
        "description": "No debería guardarse",
        "image": (io.BytesIO(b"img"), "sincat.png"),
    }
    response = client.post("/add_item/fake-cat-id",
                           data=data,
                           content_type="multipart/form-data",
                           follow_redirects=True)
    assert "Categoría no encontrada" in response.data.decode("utf-8")

import io
import pytest
from app.utils import upload_image_to_supabase


def test_upload_image_success(mocker):
    """Subida de imagen correcta"""
    # Simular archivo
    fake_file = io.BytesIO(b"fake-bytes")
    fake_file.filename = "test.png"

    # Mockear supabase
    mock_storage = mocker.Mock()
    mock_storage.upload.return_value = True
    mock_storage.get_public_url.return_value = "http://fake-url.com/test.png"

    mock_client = mocker.Mock()
    mock_client.storage.from_.return_value = mock_storage

    mocker.patch("app.utils.supabase", mock_client)

    result = upload_image_to_supabase(fake_file, folder="restaurants")
    assert result == "http://fake-url.com/test.png"


def test_upload_image_exception(mocker):
    """Error al subir imagen devuelve None"""
    fake_file = io.BytesIO(b"fake-bytes")
    fake_file.filename = "test.png"

    mock_client = mocker.Mock()
    mock_client.storage.from_.side_effect = Exception("fallo")
    mocker.patch("app.utils.supabase", mock_client)

    result = upload_image_to_supabase(fake_file, folder="restaurants")
    assert result is None


def test_upload_image_generates_unique_name(mocker):
    """El nombre generado debe contener el folder y el nombre original"""
    fake_file = io.BytesIO(b"more-bytes")
    fake_file.filename = "foto.png"

    mock_storage = mocker.Mock()
    mock_storage.upload.return_value = True
    mock_storage.get_public_url.return_value = "http://fake/foto.png"

    mock_client = mocker.Mock()
    mock_client.storage.from_.return_value = mock_storage

    mocker.patch("app.utils.supabase", mock_client)
    mock_uuid = mocker.patch("app.utils.uuid.uuid4", return_value=mocker.Mock(hex="abc123"))

    result = upload_image_to_supabase(fake_file, folder="custom-folder")

    assert "custom-folder" in result
    assert "foto.png" in result
    mock_uuid.assert_called_once()


def test_upload_image_reads_file(mocker):
    """Debe leer los bytes del archivo antes de subir"""
    fake_file = mocker.Mock()
    fake_file.filename = "doc.png"
    fake_file.read.return_value = b"123456"

    mock_storage = mocker.Mock()
    mock_storage.upload.return_value = True
    mock_storage.get_public_url.return_value = "http://fake/doc.png"

    mock_client = mocker.Mock()
    mock_client.storage.from_.return_value = mock_storage

    mocker.patch("app.utils.supabase", mock_client)

    result = upload_image_to_supabase(fake_file)
    fake_file.read.assert_called_once()
    assert result.startswith("http://fake/")


def test_register_form_valid():
    """Formulario de registro válido"""
    form = RegisterForm(
        name="Restaurante ABC",
        password="StrongPass123",
        schedule="8-4",
        location="Bogotá",
        description="Un lugar bonito"
    )
    assert form.validate() is True


def test_register_form_invalid_short_name():
    """Nombre demasiado corto"""
    form = RegisterForm(
        name="AB",
        password="StrongPass123",
        schedule="8-4",
        location="Bogotá",
        description="Desc"
    )
    assert form.validate() is False
    assert "Field must be at least 3 characters long." in form.name.errors[0]


def test_register_form_invalid_short_password():
    """Contraseña demasiado corta"""
    form = RegisterForm(
        name="Restaurante XYZ",
        password="123",
        schedule="8-4",
        location="Cali",
        description="Otro"
    )
    assert form.validate() is False
    assert "Field must be at least 6 characters long." in form.password.errors[0]


def test_register_form_missing_required_fields():
    """Campos obligatorios vacíos"""
    form = RegisterForm(
        name="",
        password="",
        schedule="",
        location="",
        description=""
    )
    assert form.validate() is False
    assert "This field is required." in form.name.errors[0]
    assert "This field is required." in form.password.errors[0]


def test_login_form_valid():
    """Formulario de login válido"""
    form = LoginForm(name="MiResto", password="Password123")
    assert form.validate() is True


def test_login_form_missing_fields():
    """Campos obligatorios faltantes en login"""
    form = LoginForm(name="", password="")
    assert form.validate() is False
    assert "This field is required." in form.name.errors[0]
    assert "This field is required." in form.password.errors[0]

#------------------------------------------------------------------------------------------------------------
def app_context():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app_context):
    return app_context.test_client()

@pytest.fixture
def user(app_context):
    user = User(id=1, username="test", email="test@test.com")
    db.session.add(user)
    db.session.commit()
    return user

def login(client, user):
    """Simula login forzando el user_id en la sesión"""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)

# ---------- TESTS DELETE CATEGORY ----------
def test_delete_category_not_owner(client, user):
    cat = Category(id=1, name="Bebidas", restaurant_id=999)
    db.session.add(cat)
    db.session.commit()

    login(client, user)
    resp = client.get("/delete_category/1", follow_redirects=True)
    assert "No tienes permiso para eliminar" in resp.get_data(as_text=True)
    assert Category.query.count() == 1  # No se eliminó

def test_delete_category_owner(client, user):
    cat = Category(id=2, name="Comida", restaurant_id=1)
    db.session.add(cat)
    db.session.commit()

    login(client, user)
    resp = client.get("/delete_category/2", follow_redirects=True)
    assert "Categoría eliminada correctamente" in resp.get_data(as_text=True)
    assert Category.query.count() == 0  # Se eliminó

# ---------- TESTS EDIT ITEM ----------
def test_edit_item_not_owner(client, user):
    item = MenuItem(id=1, name="Pizza", price=100, category_id=1, restaurant_id=999)
    db.session.add(item)
    db.session.commit()

    login(client, user)
    resp = client.post("/edit_item/1", data={"name": "Pizza X"}, follow_redirects=True)
    assert "No tienes permiso para editar" in resp.get_data(as_text=True)
    assert MenuItem.query.first().name == "Pizza"

def test_edit_item_success(client, user):
    item = MenuItem(id=2, name="Hamburguesa", price=200, category_id=1, restaurant_id=1)
    db.session.add(item)
    db.session.commit()

    login(client, user)
    resp = client.post("/edit_item/2", data={
        "name": "Hamburguesa Doble",
        "price": "300",
        "description": "Con queso"
    }, follow_redirects=True)

    assert "Platillo actualizado correctamente" in resp.get_data(as_text=True)
    updated_item = MenuItem.query.get(2)
    assert updated_item.name == "Hamburguesa Doble"
    assert updated_item.price == 300
    assert updated_item.description == "Con queso"
    
    import pytest
from flask import template_rendered

def test_get_login_page(client, captured_templates):
    with captured_templates as templates:
        response = client.get("/")
        # Verificamos que responde 200 (OK)
        assert response.status_code == 200
        # Verificamos que renderizó la plantilla correcta
        template, context = templates[0]
        assert template.name == "login.html"
