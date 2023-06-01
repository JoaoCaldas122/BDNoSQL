import cx_Oracle
from neo4j import GraphDatabase

# Connect to Oracle
oracle_conn = cx_Oracle.connect(user="store", password="pass", dsn="localhost:1521/xe")
oracle_cursor = oracle_conn.cursor()

# Connect to Neo4j
neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

# Migrate data from Oracle to Neo4j for users and sessions
oracle_cursor.execute('SELECT * FROM store_users')
users_data = oracle_cursor.fetchall()

with neo4j_driver.session() as neo4j_session:
    for user in users_data:
        user_id = user[0]
        
        # Create a user node
        neo4j_session.run(
            "CREATE (:User {user_id: $user_id, first_name: $first_name, middle_name: $middle_name, "
            "last_name: $last_name, phone_number: $phone_number, email: $email, username: $username, "
            "user_password: $user_password, registered_at: $registered_at})",
            user_id=user_id, first_name=user[1], middle_name=user[2], last_name=user[3],
            phone_number=user[4], email=user[5], username=user[6], user_password=user[7],
            registered_at=user[8]
        )
        
        # Fetch shopping sessions for the user
        oracle_cursor.execute(f"SELECT * FROM shopping_session WHERE user_id = {user_id}")
        sessions_data = oracle_cursor.fetchall()
        
        for session in sessions_data:
            session_id = session[0]
            
            # Create a session node
            neo4j_session.run(
                "MATCH (u:User {user_id: $user_id}) "
                "CREATE (u)-[:HAS_SESSION]->(:Session {session_id: $session_id, "
                "created_at: $created_at, modified_at: $modified_at})",
                user_id=user_id, session_id=session_id, created_at=session[2], modified_at=session[3]
            )
            
            # Fetch cart items for the session
            oracle_cursor.execute(f"SELECT * FROM cart_item WHERE session_id = {session_id}")
            cart_items_data = oracle_cursor.fetchall()
            
            for cart_item in cart_items_data:
                product_id = cart_item[2]
                
                # Create a cart item node
                neo4j_session.run(
                    "MATCH (s:Session {session_id: $session_id}) "
                    "CREATE (s)-[:HAS_CART_ITEM]->(:CartItem {product_id: $product_id, "
                    "quantity: $quantity, created_at: $created_at, modified_at: $modified_at})",
                    session_id=session_id, product_id=product_id, quantity=cart_item[3],
                    created_at=cart_item[4], modified_at=cart_item[5]
                )
        
        # Fetch orders for the user
        oracle_cursor.execute(f"SELECT * FROM order_details WHERE user_id = {user_id}")
        orders_data = oracle_cursor.fetchall()
        
        for order in orders_data:
            order_details_id = order[0]
            
            # Create an order node
            neo4j_session.run(
                "MATCH (u:User {user_id: $user_id}) "
                "CREATE (u)-[:PLACED_ORDER]->(:Order {order_details_id: $order_details_id, "
                "total: $total, shipping_method: $shipping_method, created_at: $created_at, "
                "modified_at: $modified_at})",
                user_id=user_id, order_details_id=order_details_id, total=order[2],
                shipping_method=order[4], created_at=order[6], modified_at=order[7]
            )
            
            # Fetch order items for the order
            oracle_cursor.execute(f"SELECT * FROM order_items WHERE ORDER_DETAILS_ID = {order_details_id}")
            order_items_data = oracle_cursor.fetchall()
            
            for item in order_items_data:
                product_id = item[2]
                
                oracle_cursor.execute(f"SELECT * FROM product WHERE product_id = {product_id}")
                products = oracle_cursor.fetchall()
                for product in products:

                    # Create a product node
                    neo4j_session.run(
                        "CREATE (:Product {product_id: $product_id, product_name: $product_name, sku: $sku, "
                        "price: $price, created_at: $created_at, last_modified: $last_modified})",
                        product_id=product[0], product_name=product[1], sku=product[3], price=product[4],
                        created_at=product[6], last_modified=product[7]
                    )           
                         
                    # Connect the order to the product with order item information
                    neo4j_session.run(
                        "MATCH (o:Order {order_details_id: $order_details_id}), "
                        "(p:Product {product_id: $product_id}) "
                        "CREATE (o)-[:HAS_PRODUCT]->(p) "
                        "SET p.created_at = $created_at, p.modified_at = $modified_at",
                        order_details_id=order_details_id, product_id=product_id,
                        created_at=item[3], modified_at=item[4]
                    )
    
# Migrate data from Oracle to Neo4j for products
oracle_cursor.execute('SELECT * FROM product')
products_data = oracle_cursor.fetchall()

with neo4j_driver.session() as neo4j_session:
    for product in products_data:
        category_id = product[2]
        discount_id = product[5]

        
        # Fetch category information
        oracle_cursor.execute(f"SELECT * FROM product_categories WHERE category_id = {category_id}")
        categories = oracle_cursor.fetchall()
        for category_data in categories:
            # Create a category node
            neo4j_session.run(
                "CREATE (:Category {category_id: $category_id, category_name: $category_name})",
                category_id=category_id,
                category_name=category_data[1]
            )

            # Create a product node
            neo4j_session.run(
                "CREATE (:Product {product_id: $product_id, product_name: $product_name, sku: $sku, "
                "price: $price, created_at: $created_at, last_modified: $last_modified})",
                product_id=product[0], product_name=product[1], sku=product[3], price=product[4],
                created_at=product[6], last_modified=product[7]
            )

            # Connect the product to its category
            neo4j_session.run(
                "MATCH (p:Product {product_id: $product_id}), (c:Category {category_id: $category_id}) "
                "CREATE (p)-[:BELONGS_TO_CATEGORY]->(c)",
                product_id=product[0], category_id=category_id
            )
        
        if discount_id is not None:
            # Fetch discount information
            oracle_cursor.execute(f"SELECT * FROM discount WHERE discount_id = {discount_id}")
            discount_data = oracle_cursor.fetchone()
            
            # Create a discount node
            neo4j_session.run(
                "MATCH (p:Product {product_id: $product_id}) "
                "CREATE (p)-[:HAS_DISCOUNT]->(:Discount {discount_id: $discount_id, "
                "discount_name: $discount_name, discount_desc: $discount_desc, "
                "discount_percent: $discount_percent, is_active_status: $is_active_status, "
                "created_at: $created_at, modified_at: $modified_at})",
                product_id=product[0], discount_id=discount_id, discount_name=discount_data[1],
                discount_desc=discount_data[2], discount_percent=discount_data[3],
                is_active_status=discount_data[4], created_at=discount_data[5],
                modified_at=discount_data[6]
            )
        
        # Fetch stock information
        oracle_cursor.execute(f"SELECT * FROM stock WHERE product_id = {product[0]}")
        stock_data = oracle_cursor.fetchone()
        
        if stock_data:
            # Create a stock node
            neo4j_session.run(
                "MATCH (p:Product {product_id: $product_id}) "
                "CREATE (p)-[:HAS_STOCK]->(:Stock {quantity: $quantity, "
                "max_stock_quantity: $max_stock_quantity, unit: $unit})",
                product_id=product[0], quantity=stock_data[1],
                max_stock_quantity=stock_data[2], unit=stock_data[3]
            )

# Migrate data from Oracle to Neo4j for employees
oracle_cursor.execute('SELECT * FROM employees')
employees_data = oracle_cursor.fetchall()

with neo4j_driver.session() as neo4j_session:
    for employee in employees_data:
        department_id = employee[5]
        manager_id = employee[11]
        
        # Fetch department information
        oracle_cursor.execute(f"SELECT * FROM departments WHERE department_id = {department_id}")
        department_data = oracle_cursor.fetchone()

        # Create a department node
        neo4j_session.run(
            "CREATE (:Department {department_id: $department_id, department_name: $department_name ,"
            "manager_id: $manager_id,department_desc: $department_desc})",
            department_id=department_data[0],
            department_name=department_data[1],
            manager_id=department_data[2],
            department_desc=department_data[3]
        )
        
        # Create an employee node
        neo4j_session.run(
            "CREATE (:Employee {employee_id: $employee_id, first_name: $first_name, "
            "middle_name: $middle_name, last_name: $last_name, date_of_birth: $date_of_birth, "
            "hire_date: $hire_date, salary: $salary, phone_number: $phone_number, "
            "email: $email, ssn_number: $ssn_number})",
            employee_id=employee[0], first_name=employee[1], middle_name=employee[2],
            last_name=employee[3], date_of_birth=employee[4], hire_date=employee[6],
            salary=employee[7], phone_number=employee[8], email=employee[9], ssn_number=employee[10]
        )
        
        # Connect the employee to the department
        neo4j_session.run(
            "MATCH (e:Employee {employee_id: $employee_id}), "
            "(d:Department {department_id: $department_id}) "
            "CREATE (e)-[:BELONGS_TO_DEPARTMENT]->(d)",
            employee_id=employee[0], department_id=department_id
        )
        
        if manager_id is not None:
            # Connect the employee to its manager
            neo4j_session.run(
                "MATCH (e:Employee {employee_id: $employee_id}), "
                "(m:Employee {employee_id: $manager_id}) "
                "CREATE (e)-[:REPORTS_TO]->(m)",
                employee_id=employee[0], manager_id=manager_id
            )
        
        # Fetch employee archive information
        oracle_cursor.execute(f"SELECT * FROM employees_archive WHERE old_employee_id = {employee[0]}")
        employee_archive_data = oracle_cursor.fetchall()
        
        for archive_entry in employee_archive_data:
            old_data = {
                'employee_id': archive_entry[3],
                'first_name': archive_entry[4],
                'middle_name': archive_entry[5],
                'last_name': archive_entry[6],
                'date_of_birth': archive_entry[7],
                'department_id': archive_entry[8],
                'hire_date': archive_entry[9],
                'salary': archive_entry[10],
                'phone_number': archive_entry[11],
                'email': archive_entry[12],
                'ssn_number': archive_entry[13],
                'manager_id': archive_entry[14]
            }
            
            new_data = {
                'employee_id': archive_entry[15],
                'first_name': archive_entry[16],
                'middle_name': archive_entry[17],
                'last_name': archive_entry[18],
                'date_of_birth': archive_entry[19],
                'department_id': archive_entry[20],
                'hire_date': archive_entry[21],
                'salary': archive_entry[22],
                'phone_number': archive_entry[23],
                'email': archive_entry[24],
                'ssn_number': archive_entry[25],
                'manager_id': archive_entry[26]
            }
            
            # Create an archive entry node and connect it to the employee
            neo4j_session.run(
                "MATCH (e:Employee {employee_id: $employee_id}) "
                "CREATE (e)-[:HAS_ARCHIVE_ENTRY]->(:ArchiveEntry {old_data: $old_data, "
                "new_data: $new_data})",
                employee_id=employee[0], old_data=old_data, new_data=new_data
            )

# Close connections
oracle_cursor.close()
oracle_conn.close()
neo4j_driver.close()
