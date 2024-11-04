from flask import Flask
from py2neo import Graph
from routes.car_routes import car_bp
from routes.customer_routes import customer_bp
from routes.employee_routes import employee_bp
from routes.special_routes import special_bp

app = Flask(__name__)

# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "Task4_yamou1685")) 

# Register blueprints
app.register_blueprint(car_bp, url_prefix='/')
app.register_blueprint(customer_bp, url_prefix='/')
app.register_blueprint(employee_bp, url_prefix='/')
app.register_blueprint(special_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)