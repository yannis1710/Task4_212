# models.py

def init_neo4j_constraints(graph):
    # Create a unique constraint for Car based on car_id
    graph.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Car) REQUIRE c.car_id IS UNIQUE")

    # Create a unique constraint for Customer based on customer_id
    graph.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE")

    # Create a unique constraint for Employee based on employee_id
    graph.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Employee) REQUIRE e.employee_id IS UNIQUE")