from app.models import MenuItem, db   
from conftest import login           


def test_edit_item_not_owner(client, user):
    # Creamos un platillo (MenuItem) que pertenece a otro restaurante (restaurant_id=999)
    item = MenuItem(id=1, name="Pizza", price=100, category_id=1, restaurant_id=999)
    db.session.add(item)    # Lo añadimos a la base de datos
    db.session.commit()     # Guardamos los cambios

    # Simulamos que el usuario hace login
    login(client, user)

    # Intentamos editar el platillo con id=1 (que NO le pertenece al usuario)
    resp = client.post("/edit_item/1", data={"name": "Pizza X"}, follow_redirects=True)

    # Verificamos que aparezca el mensaje de error por falta de permisos
    assert "No tienes permiso" in resp.get_data(as_text=True)

    # Confirmamos que el platillo NO fue modificado en la base de datos
    assert MenuItem.query.first().name == "Pizza"


def test_edit_item_success(client, user):
    # Creamos un platillo (MenuItem) que SÍ pertenece al usuario (restaurant_id=1)
    item = MenuItem(id=2, name="Hamburguesa", price=200, category_id=1, restaurant_id=1)
    db.session.add(item)    # Lo añadimos a la base de datos
    db.session.commit()     # Guardamos los cambios

    # Simulamos que el usuario hace login
    login(client, user)

    # Intentamos editar el platillo con id=2 (que sí le pertenece al usuario)
    resp = client.post("/edit_item/2", data={
        "name": "Hamburguesa Doble",   # Nuevo nombre
        "price": "300",                # Nuevo precio
        "description": "Con queso"     # Nueva descripción
    }, follow_redirects=True)

    # Verificamos que aparezca el mensaje de éxito en la respuesta
    assert "Platillo actualizado correctamente" in resp.get_data(as_text=True)

    # Confirmamos que el platillo fue actualizado en la base de datos
    updated_item = MenuItem.query.get(2)
    assert updated_item.name == "Hamburguesa Doble"
