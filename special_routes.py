from flask import Blueprint, request, jsonify
from py2neo import Graph

# Initialize the special blueprint
special_bp = Blueprint('special_bp', __name__)

# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "Task4_yamou1685"))  # Replace "your_password" with your Neo4j password

# Order a Car (POST /order-car)
@special_bp.route('/order-car', methods=['POST'])
def order_car():
    data = request.get_json()
    customer_id = data['customer_id']
    car_id = data['car_id']

    # Get the customer and car from the database
    customer = graph.nodes.match("Customer", customer_id=customer_id).first()
    car = graph.nodes.match("Car", car_id=car_id).first()

    # Check if both the customer and car exist
    if not customer or not car:
        return jsonify({'message': 'Customer or Car not found'}), 404

    # Check if the customer has already booked or rented another car
    existing_booking = graph.run("""
        MATCH (c:Customer {customer_id: $customer_id})-[:BOOKED_BY|RENTED_BY]->(car:Car)
        RETURN c
    """, customer_id=customer_id).data()

    if existing_booking:
        return jsonify({'message': 'Customer has already booked or rented a car'}), 400

    # Check if the car is available for booking
    if car['status'] != 'available':
        return jsonify({'message': 'Car is not available for booking'}), 400

    # Book the car by changing its status to 'booked'
    car['status'] = 'booked'
    graph.push(car)

    # Create the BOOKED_BY relationship
    graph.run("""
        MATCH (c:Customer {customer_id: $customer_id}), (car:Car {car_id: $car_id})
        CREATE (car)-[:BOOKED_BY]->(c)
    """, customer_id=customer_id, car_id=car_id)

    return jsonify({'message': 'Car booked successfully'})

# Cancel Car Order (POST /cancel-order-car)
@special_bp.route('/cancel-order-car', methods=['POST'])
def cancel_order_car():
    data = request.get_json()
    customer_id = data['customer_id']
    car_id = data['car_id']

    # Check if the customer has booked the car
    booking = graph.run("""
        MATCH (c:Customer {customer_id: $customer_id})<-[:BOOKED_BY]-(car:Car {car_id: $car_id})
        RETURN car
    """, customer_id=customer_id, car_id=car_id).data()

    if not booking:
        return jsonify({'message': 'No booking found for this car'}), 400

    # Cancel the booking
    car = graph.nodes.match("Car", car_id=car_id).first()
    car['status'] = 'available'
    graph.push(car)

    # Remove the BOOKED_BY relationship
    graph.run("""
        MATCH (c:Customer {customer_id: $customer_id})<-[r:BOOKED_BY]-(car:Car {car_id: $car_id})
        DELETE r
    """, customer_id=customer_id, car_id=car_id)

    return jsonify({'message': 'Car order canceled successfully'})

# Rent a Car (POST /rent-car)
@special_bp.route('/rent-car', methods=['POST'])
def rent_car():
    data = request.get_json()
    customer_id = data['customer_id']
    car_id = data['car_id']

    # Get the customer and car from the database
    customer = graph.nodes.match("Customer", customer_id=customer_id).first()
    car = graph.nodes.match("Car", car_id=car_id).first()

    if not customer or not car:
        return jsonify({'message': 'Customer or Car not found'}), 404

    # Check if the car is booked
    booking = graph.run("""
        MATCH (c:Customer {customer_id: $customer_id})<-[:BOOKED_BY]-(car:Car {car_id: $car_id})
        RETURN car
    """, customer_id=customer_id, car_id=car_id).data()

    if not booking:
        return jsonify({'message': 'No booking found for this car'}), 400

    # Rent the car
    car['status'] = 'rented'
    graph.push(car)

    # Remove the BOOKED_BY relationship and create a RENTED_BY relationship
    graph.run("""
        MATCH (c:Customer {customer_id: $customer_id})<-[r:BOOKED_BY]-(car:Car {car_id: $car_id})
        DELETE r
        CREATE (car)-[:RENTED_BY]->(c)
    """, customer_id=customer_id, car_id=car_id)

    return jsonify({'message': 'Car rented successfully'})

# Return Car (POST /return-car)
@special_bp.route('/return-car', methods=['POST'])
def return_car():
    data = request.get_json()
    customer_id = data['customer_id']
    car_id = data['car_id']
    car_status = data['status']  # 'available' or 'damaged'

    customer = graph.nodes.match("Customer", customer_id=customer_id).first()
    car = graph.nodes.match("Car", car_id=car_id).first()

    if not customer or not car:
        return jsonify({'message': 'Customer or Car not found'}), 404

    # Check if the car is rented
    rental = graph.run("""
        MATCH (c:Customer {customer_id: $customer_id})<-[:RENTED_BY]-(car:Car {car_id: $car_id})
        RETURN car
    """, customer_id=customer_id, car_id=car_id).data()

    if not rental:
        return jsonify({'message': 'No rental found for this car'}), 400

    # Update car status to 'available' or 'damaged'
    car['status'] = car_status
    graph.push(car)

    # Remove the RENTED_BY relationship
    graph.run("""
        MATCH (c:Customer {customer_id: $customer_id})<-[r:RENTED_BY]-(car:Car {car_id: $car_id})
        DELETE r
    """, customer_id=customer_id, car_id=car_id)

    return jsonify({'message': 'Car returned successfully'})

# Additional endpoints to view all data in the browser

@special_bp.route('/api/cars', methods=['GET'])
def get_all_cars():
    query = "MATCH (car:Car) RETURN car.car_id AS CarID, car.make AS Make, car.model AS Model, car.status AS Status"
    results = graph.run(query).data()
    return jsonify(results)

@special_bp.route('/api/customers', methods=['GET'])
def get_all_customers():
    query = "MATCH (customer:Customer) RETURN customer.customer_id AS CustomerID, customer.name AS Name, customer.age AS Age, customer.address AS Address"
    results = graph.run(query).data()
    return jsonify(results)

@special_bp.route('/api/employees', methods=['GET'])
def get_all_employees():
    query = "MATCH (employee:Employee) RETURN employee.employee_id AS EmployeeID, employee.name AS Name, employee.address AS Address, employee.branch AS Branch"
    results = graph.run(query).data()
    return jsonify(results)

@special_bp.route('/api/booked_cars', methods=['GET'])
def get_booked_cars():
    query = """
    MATCH (car:Car)-[:BOOKED_BY]->(customer:Customer)
    RETURN car.car_id AS CarID, car.make AS Make, car.model AS Model, car.status AS Status,
           customer.customer_id AS CustomerID, customer.name AS CustomerName
    """
    results = graph.run(query).data()
    return jsonify(results)

@special_bp.route('/api/rented_cars', methods=['GET'])
def get_rented_cars():
    query = """
    MATCH (car:Car)-[:RENTED_BY]->(customer:Customer)
    RETURN car.car_id AS CarID, car.make AS Make, car.model AS Model, car.status AS Status,
           customer.customer_id AS CustomerID, customer.name AS CustomerName
    """
    results = graph.run(query).data()
    return jsonify(results)

@special_bp.route('/fix-car', methods=['POST'])
def fix_car():
    data = request.get_json()
    car_id = data['car_id']

    # Find the car in the database
    car = graph.nodes.match("Car", car_id=car_id).first()

    # Check if the car exists
    if not car:
        return jsonify({'message': 'Car not found'}), 404

    # Check if the car is currently marked as damaged
    if car['status'] != 'damaged':
        return jsonify({'message': 'Car is not marked as damaged'}), 400

    # Update the car's status to "available" to indicate it has been fixed
    car['status'] = "available"
    graph.push(car)

    return jsonify({'message': 'Car status updated to available (repaired successfully)'})