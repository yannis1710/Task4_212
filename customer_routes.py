from flask import Blueprint, request, jsonify
from py2neo import Node, Graph

# Initialize the customer blueprint
customer_bp = Blueprint('customer_bp', __name__)

# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "Task4_yamou1685"))

# Create Customer (POST /customers)
@customer_bp.route('/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    customer = Node("Customer",
                    customer_id=data['customer_id'],
                    name=data['name'],
                    age=data['age'],
                    address=data['address'])
    graph.create(customer)
    return jsonify({'message': 'Customer created successfully'}), 201

# Get All Customers (GET /customers)
@customer_bp.route('/customers', methods=['GET'])
def get_customers():
    customers = graph.nodes.match("Customer")
    output = [dict(customer) for customer in customers]
    return jsonify({'customers': output})

# Get Customer by ID (GET /customers/<int:customer_id>)
@customer_bp.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    customer = graph.nodes.match("Customer", customer_id=customer_id).first()
    if customer:
        return jsonify(dict(customer))
    else:
        return jsonify({'message': 'Customer not found'}), 404

# Update Customer (PUT /customers/<int:customer_id>)
@customer_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.get_json()
    customer = graph.nodes.match("Customer", customer_id=customer_id).first()

    if not customer:
        return jsonify({'message': 'Customer not found'}), 404

    customer['name'] = data.get('name', customer['name'])
    customer['age'] = data.get('age', customer['age'])
    customer['address'] = data.get('address', customer['address'])

    graph.push(customer)
    return jsonify({'message': 'Customer updated successfully'})

# Delete Customer (DELETE /customers/<int:customer_id>)
@customer_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = graph.nodes.match("Customer", customer_id=customer_id).first()

    if not customer:
        return jsonify({'message': 'Customer not found'}), 404

    graph.delete(customer)
    return jsonify({'message': 'Customer deleted successfully'})