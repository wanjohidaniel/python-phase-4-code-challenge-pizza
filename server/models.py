from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref, validates
from sqlalchemy_serializer import SerializerMixin

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)

    pizzas = relationship("Pizza", secondary="restaurant_pizzas", back_populates="restaurants")

    serialize_only = ('id', 'name', 'address', 'pizzas')
    serialize_rules = ('-pizzas.restaurants',)

    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ingredients = Column(String)

    restaurants = relationship("Restaurant", secondary="restaurant_pizzas", back_populates="pizzas")

    serialize_only = ('id', 'name', 'ingredients', 'restaurants')
    serialize_rules = ('-restaurants.pizzas',)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"))
    pizza_id = Column(Integer, ForeignKey("pizzas.id", ondelete="CASCADE"))

    restaurant = relationship("Restaurant", backref=backref("restaurant_pizzas", cascade="all, delete-orphan"))
    pizza = relationship("Pizza", backref=backref("restaurant_pizzas", cascade="all, delete-orphan"))

    serialize_only = ('id', 'price', 'restaurant_id', 'pizza_id', 'restaurant', 'pizza')
    serialize_rules = ('-restaurant.pizzas', '-pizza.restaurants')

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"

    @validates('price')
    def validate_price(self, key, value):
        if not (1 <= value <= 30):
            raise ValueError('Price must be between 1 and 30')
        return value

