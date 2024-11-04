from flask import Blueprint, request, jsonify
from py2neo import Node, Graph

# Initialize the employee blueprint
employee_bp = Blueprint('employee_bp', __name__)

# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "Task4_yamou1685"))

# Create Employee (POST /employees)
@employee_bp.route('/employees', methods=['POST'])
def create_employee():
    data = request.get_json()
    employee = Node("Employee",
                    employee_id=data['employee_id'],
                    name=data['name'],
                    address=data['address'],
                    branch=data['branch'])
    graph.create(employee)
    return jsonify({'message': 'Employee created successfully'}), 201

# Get All Employees (GET /employees)
@employee_bp.route('/employees', methods=['GET'])
def get_employees():
    employees = graph.nodes.match("Employee")
    output = [dict(employee) for employee in employees]
    return jsonify({'employees': output})

# Get Employee by ID (GET /employees/<int:employee_id>)
@employee_bp.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    employee = graph.nodes.match("Employee", employee_id=employee_id).first()
    if employee:
        return jsonify(dict(employee))
    else:
        return jsonify({'message': 'Employee not found'}), 404

# Update Employee (PUT /employees/<int:employee_id>)
@employee_bp.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.get_json()
    employee = graph.nodes.match("Employee", employee_id=employee_id).first()

    if not employee:
        return jsonify({'message': 'Employee not found'}), 404

    employee['name'] = data.get('name', employee['name'])
    employee['address'] = data.get('address', employee['address'])
    employee['branch'] = data.get('branch', employee['branch'])

    graph.push(employee)
    return jsonify({'message': 'Employee updated successfully'})

# Delete Employee (DELETE /employees/<int:employee_id>)
@employee_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    employee = graph.nodes.match("Employee", employee_id=employee_id).first()

    if not employee:
        return jsonify({'message': 'Employee not found'}), 404

    graph.delete(employee)
    return jsonify({'message': 'Employee deleted successfully'})