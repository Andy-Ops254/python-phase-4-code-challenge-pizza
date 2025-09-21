#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants')
def get_restaurant():
    restaurants = []
    for restaurant in Restaurant.query.all():
        restaurant_dict= restaurant.to_dict(only=('id','name','address'))
        restaurants.append(restaurant_dict)
    response = make_response(
            restaurants,
            200
        )
    return response

@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def restaurants_by_id(id):
    if request.method == 'GET':
        restaurant = Restaurant.query.filter_by(id=id).first()

        if restaurant:
            restaurant_dict = restaurant.to_dict()
            response = make_response(
                restaurant_dict,
                200
            )
            return response
        else:
            response = make_response(
                {"error": "Restaurant not found"},
                404
            )
            return response
    
    if request.method =='DELETE':
        restaurant = Restaurant.query.filter_by(id=id).first()

        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            # response_body={
            #     'delete_successfully': True,
            #     "Message": "Restaurant deleted successfully"
            # }
            response= make_response(
                {},
                204
            )
            return response
        else:
            response = make_response(
                {"error": "Restaurant not found"},
                404
            )
            return response
        

@app.route('/pizzas')
def get_pizzas():
    pizzas = []
    for pizza in Pizza.query.all():
        pizza_dict = pizza.to_dict(only=('id', 'ingredients', 'name'))
        pizzas.append(pizza_dict)
    response = make_response(
        pizzas,
        200
    )
    return response

@app.route('/restaurant_pizzas', methods=['POST'])
def new_restaurant_pizzas():
    data = request.get_json()
    if not data:
        return make_response({"errors": ["No data provided"]}, 400)
    
    # Check if required fields exist
    if not data.get('price') or not data.get('pizza_id') or not data.get('restaurant_id'):
        return make_response({"errors": ["validation errors"]}, 400)
    try:
        new_restaurant_pizzas = RestaurantPizza(
            price =request.json.get("price"),
            pizza_id = request.json.get("pizza_id"),
            restaurant_id = request.json.get("restaurant_id")
        )
        db.session.add(new_restaurant_pizzas)
        db.session.commit()
        pizza = Pizza.query.get(new_restaurant_pizzas.pizza_id)
        restaurant = Restaurant.query.get(new_restaurant_pizzas.restaurant_id)

        response_data = {
                "id": new_restaurant_pizzas.id,
                "price": new_restaurant_pizzas.price,
                "pizza_id": new_restaurant_pizzas.pizza_id,
                "restaurant_id": new_restaurant_pizzas.restaurant_id,
                "pizza": pizza.to_dict(only=('id', 'name', 'ingredients')),
                "restaurant": restaurant.to_dict(only=('id', 'name', 'address'))
            }
        return make_response(response_data, 201)
    
    except ValueError as e:
        return make_response({"errors": [str(e)]}, 400)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
