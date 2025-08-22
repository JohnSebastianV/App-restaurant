from . import db, login_manager
from flask_login import UserMixin
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

class Restaurant(UserMixin, db.Model):
    __tablename__ = "restaurants"
    __table_args__ = {"schema": "restaurant"}

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    schedule = db.Column(db.String(255))
    location = db.Column(db.String(255))
    image = db.Column(db.String(255))
    description = db.Column(db.Text)

    categories = db.relationship("Category", back_populates="restaurant", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = {"schema": "restaurant"}

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    category = db.Column(db.String(120), nullable=False)

    restaurant_id = db.Column(db.String, db.ForeignKey("restaurant.restaurants.id"), nullable=False)
    restaurant = db.relationship("Restaurant", back_populates="categories")

    items = db.relationship("MenuItem", back_populates="category", cascade="all, delete-orphan")


class MenuItem(db.Model):
    __tablename__ = "menu_items"
    __table_args__ = {"schema": "restaurant"}

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255))
    description = db.Column(db.Text)

    category_id = db.Column(db.String, db.ForeignKey("restaurant.categories.id"), nullable=False)
    category = db.relationship("Category", back_populates="items")


@login_manager.user_loader
def load_user(user_id):
    return Restaurant.query.get(user_id)
