from flask import Blueprint, request, jsonify
from py2neo import Node, Graph

# Initialize the car blueprint
car_bp = Blueprint('car_bp', __name__)

# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "Task4_yamou1685"))

# Create Car (POST /cars)
@car_bp.route('/cars', methods=['POST'])
def create_car():
    data = request.get_json()
    car = Node("Car",
               car_id=data['car_id'],
               make=data['make'],
               model=data['model'],
               year=data['year'],
               location=data['location'],
               status=data.get('status', 'available'))
    graph.create(car)
    return jsonify({'message': 'Car created successfully'}), 201

# Get All Cars (GET /cars)
@car_bp.route('/cars', methods=['GET'])
def get_cars():
    cars = graph.nodes.match("Car")
    output = [dict(car) for car in cars]
    return jsonify({'cars': output})

# Get Car by ID (GET /cars/<int:car_id>)
@car_bp.route('/cars/<int:car_id>', methods=['GET'])
def get_car(car_id):
    car = graph.nodes.match("Car", car_id=car_id).first()
    if car:
        return jsonify(dict(car))
    else:
        return jsonify({'message': 'Car not found'}), 404

# Update Car (PUT /cars/<int:car_id>)
@car_bp.route('/cars/<int:car_id>', methods=['PUT'])
def update_car(car_id):
    data = request.get_json()
    car = graph.nodes.match("Car", car_id=car_id).first()

    if not car:
        return jsonify({'message': 'Car not found'}), 404

    car['make'] = data.get('make', car['make'])
    car['model'] = data.get('model', car['model'])
    car['year'] = data.get('year', car['year'])
    car['location'] = data.get('location', car['location'])
    car['status'] = data.get('status', car['status'])

    graph.push(car)
    return jsonify({'message': 'Car updated successfully'})

# Delete Car (DELETE /cars/<int:car_id>)
@car_bp.route('/cars/<int:car_id>', methods=['DELETE'])
def delete_car(car_id):
    car = graph.nodes.match("Car", car_id=car_id).first()

    if not car:
        return jsonify({'message': 'Car not found'}), 404

    graph.delete(car)
    return jsonify({'message': 'Car deleted successfully'})