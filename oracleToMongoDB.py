import cx_Oracle
from pymongo import MongoClient

# Connect to Oracle
oracle_conn = cx_Oracle.connect(user="uminho", password="uminho2020", dsn="localhost:1521/xe")
oracle_cursor = oracle_conn.cursor()

# Connect to MongoDB
mongo_client = MongoClient('mongodb://localhost:27017')
mongo_db = mongo_client['tpnosql']
users_collection = mongo_db['users']
products_collection = mongo_db['products']
employees_collection = mongo_db['employees']

# Migrate data from Oracle to MongoDB for users collection
oracle_cursor.execute('SELECT * FROM store_users')
users_data = oracle_cursor.fetchall()

for user in users_data:
    user_id = user['user_id']
    sessions = []
    
    # Fetch shopping sessions for the user
    oracle_cursor.execute(f"SELECT * FROM shopping_session WHERE user_id = {user_id}")
    sessions_data = oracle_cursor.fetchall()
    
    for session in sessions_data:
        session_id = session['session_id']
        cart_items = []
        
        # Fetch cart items for the session
        oracle_cursor.execute(f"SELECT * FROM cart_item WHERE session_id = {session_id}")
        cart_items_data = oracle_cursor.fetchall()
        
        for cart_item in cart_items_data:
            product_id = cart_item['product_id']
            
            # Create a cart item document
            cart_item_doc = {
                'product_id': product_id,
                'quantity': cart_item['quantity'],
                'created_at': cart_item['created_at'],
                'modified_at': cart_item['modified_at']
            }
            cart_items.append(cart_item_doc)
        
        # Create a session document
        session_doc = {
            'session_id': session_id,
            'created_at': session['created_at'],
            'modified_at': session['modified_at'],
            'cart_items': cart_items
        }
        sessions.append(session_doc)
    
    # Create a user document
    user_doc = {
        'user_id': user_id,
        'first_name': user['first_name'],
        'middle_name': user['middle_name'],
        'last_name': user['last_name'],
        'phone_number': user['phone_number'],
        'email': user['email'],
        'username': user['username'],
        'user_password': user['user_password'],
        'registered_at': user['registered_at'],
        'sessions': sessions
    }
    
    # Insert the user document into the users collection
    users_collection.insert_one(user_doc)

# Migrate data from Oracle to MongoDB for products collection
oracle_cursor.execute('SELECT * FROM product')
products_data = oracle_cursor.fetchall()

for product in products_data:
    category_id = product['category_id']
    discount_id = product['discount_id']
    
    # Fetch category information
    oracle_cursor.execute(f"SELECT * FROM product_categories WHERE category_id = {category_id}")
    category_data = oracle_cursor.fetchone()
    
    if discount_id is not None:
        # Fetch discount information
        oracle_cursor.execute(f"SELECT * FROM discount WHERE discount_id = {discount_id}")
        discount_data = oracle_cursor.fetchone()
        
        # Create a product document
        product_doc = {
            'product_id': product['product_id'],
            'product_name': product['product_name'],
            'sku': product['sku'],
            'price': product['price'],
            'created_at': product['created_at'],
            'last_modified': product['last_modified'],
            'category': {
                'category_id': category_id,
                'category_name': category_data['category_name']
            },
            'discount': {
                'discount_id': discount_id,
                'discount_name': discount_data['discount_name'],
                'discount_desc': discount_data['discount_desc'],
                'discount_percent': discount_data['discount_percent'],
                'is_active_status': discount_data['is_active_status'],
                'created_at': discount_data['created_at'],
                'modified_at': discount_data['modified_at']
            },
            'stock': {
                'quantity': None,
                'max_stock_quantity': None,
                'unit': None
            }
        }
        
        # Fetch stock information
        oracle_cursor.execute(f"SELECT * FROM stock WHERE product_id = {product['product_id']}")
        stock_data = oracle_cursor.fetchone()
        
        if stock_data:
            product_doc['stock']['quantity'] = stock_data['quantity']
            product_doc['stock']['max_stock_quantity'] = stock_data['max_stock_quantity']
            product_doc['stock']['unit'] = stock_data['unit']
    else:
        # Create a product document without discount information
        product_doc = {
            'product_id': product['product_id'],
            'product_name': product['product_name'],
            'sku': product['sku'],
            'price': product['price'],
            'created_at': product['created_at'],
            'last_modified': product['last_modified'],
            'category': {
                'category_id': category_id,
                'category_name': category_data['category_name']
            },
            'stock': {
                'quantity': None,
                'max_stock_quantity': None,
                'unit': None
            }
        }
        
        # Fetch stock information
        oracle_cursor.execute(f"SELECT * FROM stock WHERE product_id = {product['product_id']}")
        stock_data = oracle_cursor.fetchone()
        
        if stock_data:
            product_doc['stock']['quantity'] = stock_data['quantity']
            product_doc['stock']['max_stock_quantity'] = stock_data['max_stock_quantity']
            product_doc['stock']['unit'] = stock_data['unit']
    
    # Insert the product document into the products collection
    products_collection.insert_one(product_doc)

# Migrate data from Oracle to MongoDB for employees collection
oracle_cursor.execute('SELECT * FROM employees')
employees_data = oracle_cursor.fetchall()

for employee in employees_data:
    department_id = employee['department_id']
    manager_id = employee['manager_id']
    
    # Fetch department information
    oracle_cursor.execute(f"SELECT * FROM departments WHERE department_id = {department_id}")
    department_data = oracle_cursor.fetchone()
    
    # Create an employee document
    employee_doc = {
        'employee_id': employee['employee_id'],
        'first_name': employee['first_name'],
        'middle_name': employee['middle_name'],
        'last_name': employee['last_name'],
        'date_of_birth': employee['date_of_birth'],
        'hire_date': employee['hire_date'],
        'salary': employee['salary'],
        'phone_number': employee['phone_number'],
        'email': employee['email'],
        'ssn_number': employee['ssn_number'],
        'manager_id': manager_id,
        'department': {
            'department_id': department_id,
            'department_name': department_data['department_name'],
            'manager_id': department_data['manager_id'],
            'department_desc': department_data['department_desc']
        },
        'employees_archive': []
    }
    
    # Fetch employee archive information
    oracle_cursor.execute(f"SELECT * FROM employees_archive WHERE old_employee_id = {employee['employee_id']}")
    employee_archive_data = oracle_cursor.fetchall()
    
    for archive_entry in employee_archive_data:
        old_data = {
            'employee_id': archive_entry['old_employee_id'],
            'first_name': archive_entry['old_first_name'],
            'middle_name': archive_entry['old_middle_name'],
            'last_name': archive_entry['old_last_name'],
            'date_of_birth': archive_entry['old_date_of_birth'],
            'department_id': archive_entry['old_department_id'],
            'hire_date': archive_entry['old_hire_date'],
            'salary': archive_entry['old_salary'],
            'phone_number': archive_entry['old_phone_number'],
            'email': archive_entry['old_email'],
            'ssn_number': archive_entry['old_ssn_number'],
            'manager_id': archive_entry['old_manager_id']
        }
        
        new_data = {
            'employee_id': archive_entry['new_employee_id'],
            'first_name': archive_entry['new_first_name'],
            'middle_name': archive_entry['new_middle_name'],
            'last_name': archive_entry['new_last_name'],
            'date_of_birth': archive_entry['new_date_of_birth'],
            'department_id': archive_entry['new_department_id'],
            'hire_date': archive_entry['new_hire_date'],
            'salary': archive_entry['new_salary'],
            'phone_number': archive_entry['new_phone_number'],
            'email': archive_entry['new_email'],
            'ssn_number': archive_entry['new_ssn_number'],
            'manager_id': archive_entry['new_manager_id']
        }
        
        archive_entry_doc = {
            'event_date': archive_entry['event_date'],
            'event_type': archive_entry['event_type'],
            'user_name': archive_entry['user_name'],
            'old_data': old_data,
            'new_data': new_data
        }
        
        employee_doc['employees_archive'].append(archive_entry_doc)
    
    # Insert the employee document into the employees collection
    employees_collection.insert_one(employee_doc)
    
# Close the Oracle cursor and connection
oracle_cursor.close()
oracle_conn.close()

# Close the MongoDB client
mongo_client.close()

