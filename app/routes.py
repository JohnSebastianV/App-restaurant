import re
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.utils import upload_image_to_supabase
from .forms import RegisterForm, LoginForm
from .models import db, Restaurant, Category, MenuItem

bp = Blueprint("main", __name__, template_folder="../templates")

# Página inicial -> muestra login si no hay sesión
@bp.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        restaurant = Restaurant.query.filter_by(name=form.name.data).first()
        if restaurant and restaurant.check_password(form.password.data):
            login_user(restaurant)
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Nombre o contraseña incorrectos.", "danger")

    return render_template("login.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        restaurant = Restaurant.query.filter_by(name=form.name.data).first()
        if restaurant and restaurant.check_password(form.password.data):
            login_user(restaurant)
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Nombre o contraseña incorrectos.", "danger")
    return render_template("login.html", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        password = request.form["password"].strip()
        schedule = request.form["schedule"].strip()
        location = request.form["location"].strip()
        description = request.form["description"].strip()
        file = request.files.get("image")

        if not all([name, password, schedule, location, description, file]):
            flash("Todos los campos son obligatorios (incluyendo la imagen).", "danger")
            return redirect(url_for("main.register"))

        existing_restaurant = Restaurant.query.filter_by(name=name).first()
        if existing_restaurant:
            flash("Ese nombre de restaurante ya está registrado. Intenta con otro.", "danger")
            return redirect(url_for("main.register"))

        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', password):
            flash("La contraseña debe tener al menos 8 caracteres, incluyendo una mayúscula, una minúscula y un número.", "danger")
            return redirect(url_for("main.register"))

        image_url = upload_image_to_supabase(file, folder="restaurants")

        new_restaurant = Restaurant(
            name=name,
            schedule=schedule,
            location=location,
            description=description,
            image=image_url,
        )
        new_restaurant.set_password(password)

        db.session.add(new_restaurant)
        db.session.commit()

        flash("Restaurante registrado con éxito ✅", "success")
        return redirect(url_for("main.index"))

    return render_template("register.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", restaurant=current_user)


@bp.route("/add_category", methods=["POST"])
@login_required
def add_category():
    category_name = request.form.get("category")
    if category_name:
        category = Category(category=category_name, restaurant_id=current_user.id)
        db.session.add(category)
        db.session.commit()
        flash("Categoría agregada correctamente.", "success")
    return redirect(url_for("main.dashboard"))


@bp.route("/add_item/<string:category_id>", methods=["GET", "POST"])
@login_required
def add_item(category_id):
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        description = request.form["description"]
        file = request.files.get("image")

        image_url = upload_image_to_supabase(file, folder="menu") if file else None

        new_item = MenuItem(
            name=name,
            price=price,
            description=description,
            image=image_url,
            category_id=category_id
        )

        db.session.add(new_item)
        db.session.commit()

        flash("Plato agregado con éxito", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("add_item.html", category_id=category_id)


@bp.route("/edit_category/<string:category_id>", methods=["POST"])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)

    if category.restaurant_id != current_user.id:
        flash("No tienes permiso para editar esta categoría.", "danger")
        return redirect(url_for("main.dashboard"))

    new_name = request.form.get("category")
    if new_name:
        category.category = new_name
        db.session.commit()
        flash("Categoría actualizada correctamente ✅", "success")

    return redirect(url_for("main.dashboard"))


@bp.route("/delete_category/<string:category_id>", methods=["POST"])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    if category.restaurant_id != current_user.id:
        flash("No tienes permiso para eliminar esta categoría.", "danger")
        return redirect(url_for("main.dashboard"))

    db.session.delete(category)
    db.session.commit()
    flash("Categoría eliminada correctamente 🗑️", "success")

    return redirect(url_for("main.dashboard"))


@bp.route("/edit_item/<string:item_id>", methods=["POST"])
@login_required
def edit_item(item_id):
    item = MenuItem.query.get_or_404(item_id)

    if item.category.restaurant_id != current_user.id:
        flash("No tienes permiso para editar este platillo.", "danger")
        return redirect(url_for("main.dashboard"))

    item.name = request.form.get("name")
    item.price = request.form.get("price")
    item.description = request.form.get("description")

    file = request.files.get("image")
    if file:
        item.image = upload_image_to_supabase(file, folder="menu_items")

    db.session.commit()
    flash("Platillo actualizado correctamente ✅", "success")
    return redirect(url_for("main.dashboard"))


@bp.route("/delete_item/<string:item_id>", methods=["POST"])
@login_required
def delete_item(item_id):
    item = MenuItem.query.get_or_404(item_id)

    if item.category.restaurant_id != current_user.id:
        flash("No tienes permiso para eliminar este platillo.", "danger")
        return redirect(url_for("main.dashboard"))

    db.session.delete(item)
    db.session.commit()
    flash("Platillo eliminado correctamente 🗑️", "success")

    return redirect(url_for("main.dashboard"))


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("main.index"))
