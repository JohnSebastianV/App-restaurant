import io
import pytest
from app.models import Restaurant


@pytest.fixture
def client(app):
    # Configuramos la aplicación en modo TEST
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Desactivamos CSRF en los formularios
    return app.test_client()  # Cliente de pruebas de Flask


def test_register_restaurant(client, mocker):
    # Simulamos que la función de subida de imágenes devuelve una URL falsa
    mocker.patch("app.routes.upload_image_to_supabase",
                 return_value="http://fake.url/image.png")

    # Simulamos que no existe ningún restaurante con el mismo nombre
    mocker.patch("app.models.Restaurant.query.filter_by",
                 return_value=mocker.Mock(first=lambda: None))
    # Evitamos que realmente se inserte en la BD
    mocker.patch("app.db.session.add")
    mocker.patch("app.db.session.commit")

    # Datos válidos para registrar un restaurante
    data = {
        "name": "NuevoRest",
        "password": "Password123",
        "schedule": "8-4",
        "location": "Bogotá",
        "description": "Un restaurante nuevo",
        "image": (io.BytesIO(b"fake-image-data"), "resto.png"),
    }
    # Enviamos la petición POST al endpoint de registro
    response = client.post("/register",
                           data=data,
                           content_type="multipart/form-data",
                           follow_redirects=True)

    # Verificamos que aparece el mensaje de éxito
    assert "Restaurante registrado con éxito" in response.data.decode("utf-8")


def test_register_missing_fields(client):
    # Datos con campos vacíos
    data = {
        "name": "",
        "password": "",
        "schedule": "",
        "location": "",
        "description": "",
    }
    # Enviamos el formulario incompleto
    response = client.post("/register", data=data, follow_redirects=True)

    # Verificamos que aparece el mensaje de error por campos faltantes
    assert "Todos los campos son obligatorios" in response.data.decode("utf-8")


def test_register_invalid_password(client, mocker):
    # Simulamos que no existe ningún restaurante con el mismo nombre
    mocker.patch("app.models.Restaurant.query.filter_by",
                 return_value=mocker.Mock(first=lambda: None))

    # Datos con contraseña débil (no cumple requisitos)
    data = {
        "name": "WeakRest",
        "password": "weak",  # Contraseña inválida
        "schedule": "8-4",
        "location": "Cali",
        "description": "Desc",
        "image": (io.BytesIO(b"fake"), "weak.png"),
    }
    # Enviamos la petición POST con datos inválidos
    response = client.post("/register",
                           data=data,
                           content_type="multipart/form-data",
                           follow_redirects=True)

    # Verificamos que aparece el mensaje de contraseña inválida
    assert "La contraseña debe tener" in response.data.decode("utf-8")


def test_register_duplicate_restaurant(client, mocker):
    # Creamos un restaurante ficticio que ya existe en la BD
    fake_restaurant = Restaurant(name="Duplicado", schedule="9-5",
                                 location="City", description="desc", image="url")
    # Simulamos que la consulta devuelve ese restaurante existente
    mocker.patch("app.models.Restaurant.query.filter_by",
                 return_value=mocker.Mock(first=lambda: fake_restaurant))

    # Datos que intentan registrar un restaurante duplicado
    data = {
        "name": "Duplicado",
        "password": "Password123",
        "schedule": "9-5",
        "location": "Medellín",
        "description": "resto",
        "image": (io.BytesIO(b"fake-img"), "dup.png"),
    }
    # Enviamos la petición POST con datos duplicados
    response = client.post("/register",
                           data=data,
                           content_type="multipart/form-data",
                           follow_redirects=True)

    # Verificamos que aparece el mensaje de restaurante ya registrado
    assert "ya está registrado" in response.data.decode("utf-8")
