import pytest
from app.models import Restaurant


@pytest.fixture
def client(app):
    # Configuramos la aplicación en modo TEST
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Desactivamos CSRF para simplificar los tests
    return app.test_client()  # Retornamos el cliente de pruebas de Flask


def test_login_invalid_credentials(client, mocker):
    # Creamos un restaurante ficticio en memoria
    fake_restaurant = Restaurant(name="RestFail", schedule="9-5",
                                 location="TestCity", description="test", image="url")
    fake_restaurant.set_password("Password123")  # Asignamos una contraseña válida

    # Simulamos que la consulta devuelve este restaurante
    mocker.patch("app.models.Restaurant.query.filter_by",
                 return_value=mocker.Mock(first=lambda: fake_restaurant))
    # Simulamos que la verificación de contraseña siempre falla
    mocker.patch.object(fake_restaurant, "check_password", return_value=False)

    # Intentamos hacer login con credenciales incorrectas
    response = client.post("/login",
                           data={"name": "RestFail", "password": "wrong"},
                           follow_redirects=True)

    # Verificamos que el sistema muestra un mensaje de error de credenciales
    assert "incorrectos" in response.data.decode("utf-8")


def test_login_nonexistent_user(client, mocker):
    # Simulamos que la consulta no encuentra ningún restaurante
    mocker.patch("app.models.Restaurant.query.filter_by",
                 return_value=mocker.Mock(first=lambda: None))

    # Intentamos hacer login con un usuario que no existe
    response = client.post("/login",
                           data={"name": "NoExiste", "password": "1234"},
                           follow_redirects=True)

    # Verificamos que aparece el mensaje de credenciales incorrectas
    assert "incorrectos" in response.data.decode("utf-8")


def test_logout(client, mocker):
    # Creamos un restaurante ficticio y lo simulamos como usuario logueado
    fake_restaurant = mocker.Mock()
    fake_restaurant.id = "rest-123"
    mocker.patch("flask_login.utils._get_user", return_value=fake_restaurant)

    # Hacemos la petición para cerrar sesión
    response = client.get("/logout", follow_redirects=True)

    # Verificamos que aparece el mensaje de cierre de sesión
    assert "Sesión cerrada" in response.data.decode("utf-8")
