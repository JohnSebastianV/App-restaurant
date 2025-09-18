from app.models import Category, db  
from conftest import login          

def test_delete_category_not_owner(client, user):
    # Creamos una categoría que pertenece a otro restaurante (restaurant_id=999)
    cat = Category(id=1, name="Bebidas", restaurant_id=999)
    db.session.add(cat)    # La añadimos a la base de datos
    db.session.commit()    # Guardamos los cambios

    # Simulamos que el usuario hace login
    login(client, user)

    # Intentamos eliminar la categoría con id=1 (que no le pertenece al usuario)
    resp = client.get("/delete_category/1", follow_redirects=True)

    # Verificamos que aparezca el mensaje de error de permisos
    assert "No tienes permiso" in resp.get_data(as_text=True)

    # Confirmamos que la categoría no fue eliminada y sigue existiendo en la BD
    assert Category.query.count() == 1


def test_delete_category_owner(client, user):
    # Creamos una categoría que sí pertenece al usuario (restaurant_id=1)
    cat = Category(id=2, name="Comida", restaurant_id=1)
    db.session.add(cat)    # La añadimos a la base de datos
    db.session.commit()    # Guardamos los cambios

    # Simulamos que el usuario hace login
    login(client, user)

    # Intentamos eliminar la categoría con id=2 (que sí le pertenece al usuario)
    resp = client.get("/delete_category/2", follow_redirects=True)

    # Verificamos que aparezca el mensaje de éxito al eliminar
    assert "Categoría eliminada correctamente" in resp.get_data(as_text=True)

    # Confirmamos que la categoría fue eliminada de la base de datos
    assert Category.query.count() == 0
