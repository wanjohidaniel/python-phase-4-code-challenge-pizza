import os
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_migrate import Migrate
from models import db, Restaurant, RestaurantPizza, Pizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-RESTful API
api = Api(app)

# Index route
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# RESTful resource for all restaurants
class RestaurantsResource(Resource):
    def get(self):
        try:
            restaurants = Restaurant.query.all()
            return jsonify([restaurant.to_dict() for restaurant in restaurants]), 200
        except Exception as e:
            app.logger.error(f"Error retrieving restaurants: {e}")
            return jsonify({"error": str(e)}), 500

# RESTful resource for a single restaurant
class RestaurantResource(Resource):
    def get(self, id):
        try:
            restaurant = Restaurant.query.get(id)
            if not restaurant:
                return jsonify({"error": "Restaurant not found"}), 404
            return jsonify(restaurant.to_dict(include_relationships=True)), 200
        except Exception as e:
            app.logger.error(f"Error retrieving restaurant {id}: {e}")
            return jsonify({"error": str(e)}), 500

# Route for getting all restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    try:
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants]), 200
    except Exception as e:
        app.logger.error(f"Error retrieving restaurants: {e}")
        return jsonify({"error": str(e)}), 500

# Route for getting a single restaurant by ID
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404
        
        restaurant_data = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'restaurant_pizzas': []
        }
        for rp in restaurant.restaurant_pizzas:
            pizza_data = {
                'id': rp.id,
                'pizza': {
                    'id': rp.pizza.id,
                    'name': rp.pizza.name,
                    'ingredients': rp.pizza.ingredients
                },
                'price': rp.price
            }
            restaurant_data['restaurant_pizzas'].append(pizza_data)
        
        return jsonify(restaurant_data), 200
    except Exception as e:
        app.logger.error(f"Error retrieving restaurant {id}: {e}")
        return jsonify({'error': str(e)}), 500

# Route for deleting a restaurant by ID
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
        
        RestaurantPizza.query.filter_by(restaurant_id=id).delete()
        db.session.delete(restaurant)
        db.session.commit()
        
        return "", 204
    except Exception as e:
        app.logger.error(f"Error deleting restaurant {id}: {e}")
        return jsonify({"error": str(e)}), 500

# Route for getting all pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    try:
        pizzas = Pizza.query.all()
        pizza_data = []
        for pizza in pizzas:
            pizza_info = {
                'id': pizza.id,
                'name': pizza.name,
                'ingredients': pizza.ingredients
            }
            pizza_data.append(pizza_info)
        
        return jsonify(pizza_data), 200
    except Exception as e:
        app.logger.error(f"Error retrieving pizzas: {e}")
        return jsonify({"error": str(e)}), 500
        
# Route for creating restaurant pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizzas():
    try:
        data = request.json
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")
        price = data.get("price")

        if not all([pizza_id, restaurant_id, price is not None]):
            return jsonify({"error": "Missing data fields"}), 400
        
        if not isinstance(price, int) or not (1 <= price <= 30):
            return jsonify({"error": "Price must be an integer between 1 and 30"}), 400

        restaurant_pizza = RestaurantPizza(
            pizza_id=pizza_id, restaurant_id=restaurant_id, price=price
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        return jsonify(restaurant_pizza.to_dict()), 201  # Return 201 Created status
    except Exception as e:
        app.logger.error(f"Error creating restaurant pizza: {e}")
        return jsonify({"error": str(e)}), 400

# Register RESTful resources
api.add_resource(RestaurantsResource, "/restaurants")
api.add_resource(RestaurantResource, "/restaurants/<int:id>")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
