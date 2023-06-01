import cx_Oracle
from pymongo import MongoClient

# Connect to Oracle
oracle_conn = cx_Oracle.connect(user="uminho", password="uminho2020", dsn="localhost:1521/xe")
oracle_cursor = oracle_conn.cursor()

url = 'Metam o link'

mongo_client = MongoClient(url)
mongo_db = mongo_client['tpnosql']
users_collection = mongo_db['users']
products_collection = mongo_db['products']
employees_collection = mongo_db['employees']

# Migrate data from Oracle to MongoDB for users collection
oracle_cursor.execute('SELECT * FROM store_users')
users_data = oracle_cursor.fetchall()

for user in users_data:
    user_id = user[0]
    sessions = []
    
    # Fetch shopping sessions for the user
    oracle_cursor.execute(f"SELECT * FROM shopping_session WHERE user_id = {user_id}")
    sessions_data = oracle_cursor.fetchall()
    
    for session in sessions_data:
        session_id = session[0]
        cart_items = []
        
        # Fetch cart items for the session
        oracle_cursor.execute(f"SELECT * FROM cart_item WHERE session_id = {session_id}")
        cart_items_data = oracle_cursor.fetchall()
        for cart_item in cart_items_data:
            
            product_id = cart_item[2]
            
            # Create a cart item document
            cart_item_doc = {
                'product_id': product_id,
                'quantity': cart_item[3],
                'created_at': cart_item[4],
                'modified_at': cart_item[5]
            }
            cart_items.append(cart_item_doc)
        
        # Create a session document
        session_doc = {
            'session_id': session_id,
            'created_at': session[2],
            'modified_at': session[3],
            'cart_items': cart_items
        }
        sessions.append(session_doc)

    oracle_cursor.execute(f"SELECT * FROM order_details WHERE user_id = {user_id}")
    orders_data = oracle_cursor.fetchall()

    orders = []

    for order in orders_data:
        order_details_id = order[0]

        order_items = []

        oracle_cursor.execute(f"SELECT * FROM order_items WHERE ORDER_DETAILS_ID = {order_details_id}")
        order_items_data = oracle_cursor.fetchall()

        for item in order_items_data:
            order_item_doc = {
                'order_item_id': cart_item[0],
                'product_id': cart_item[2],
                'created_at': cart_item[3],
                'modified_at': cart_item[4]
            }
            
            order_items.append(order_item_doc)

        oracle_cursor.execute(f"SELECT * FROM ADDRESSES WHERE adress_id = {order[5]}")
        delivery_data = oracle_cursor.fetchall()[0]

        delivery_doc = {
            'line_1': delivery_data[1],
            'line_2': delivery_data[2],
            'city': delivery_data[3],
            'zip_code': delivery_data[4],
            'province': delivery_data[5],
            'country': delivery_data[6]
        }

        oracle_cursor.execute(f"SELECT * FROM payment_details WHERE order_id = {order_details_id}")
        payment = oracle_cursor.fetchall()[0]
        payment_doc = {
                'payment_id':payment[0],
                'order_id':order_details_id,
                'amount':payment[2],
                'provider':payment[3],
                'payment_status':payment[4],
                'created_at':payment[5],
                'modified_at':payment[6]
            }

        
        order_doc = {
            'order_details_id': order_details_id,
            'total': order[2],
            'payment': payment_doc,
            'shipping_method': order[4],
            'delivery_adress': delivery_doc,
            'created_at': order[6],
            'modified_at': order[7],
            'order_items': order_items
        }

        orders.append(order_doc)
    
    # Create a user document
    user_doc = {
        'user_id': user_id,
        'first_name': user[1],
        'middle_name': user[2],
        'last_name': user[3],
        'phone_number': user[4],
        'email': user[5],
        'username': user[6],
        'user_password': user[7],
        'registered_at': user[8],
        'sessions': sessions,
        'orders': orders
    }
    
    # Insert the user document into the users collection
    users_collection.insert_one(user_doc)

# Migrate data from Oracle to MongoDB for products collection
oracle_cursor.execute('SELECT * FROM product')
products_data = oracle_cursor.fetchall()

for product in products_data:
    category_id = product[2]
    discount_id = product[5]
    
    # Fetch category information
    oracle_cursor.execute(f"SELECT * FROM product_categories WHERE category_id = {category_id}")
    category_data = oracle_cursor.fetchone()
    
    if discount_id is not None:
        # Fetch discount information
        oracle_cursor.execute(f"SELECT * FROM discount WHERE discount_id = {discount_id}")
        discount_data = oracle_cursor.fetchone()
        
        # Create a product document
        product_doc = {
            'product_id': product[0],
            'product_name': product[1],
            'sku': product[3],
            'price': product[4],
            'created_at': product[6],
            'last_modified': product[7],
            'category': {
                'category_id': category_id,
                'category_name': category_data[1]
            },
            'discount': {
                'discount_id': discount_id,
                'discount_name': discount_data[1],
                'discount_desc': discount_data[2],
                'discount_percent': discount_data[3],
                'is_active_status': discount_data[4],
                'created_at': discount_data[5],
                'modified_at': discount_data[6]
            },
            'stock': {
                'quantity': None,
                'max_stock_quantity': None,
                'unit': None
            }
        }
        
        # Fetch stock information
        oracle_cursor.execute(f"SELECT * FROM stock WHERE product_id = {product[0]}")
        stock_data = oracle_cursor.fetchone()

        if stock_data:
            product_doc['stock']['quantity'] = stock_data[1]
            product_doc['stock']['max_stock_quantity'] = stock_data[2]
            product_doc['stock']['unit'] = stock_data[3]
    else:
        # Create a product document without discount information
        product_doc = {
            'product_id': product[0],
            'product_name': product[1],
            'sku': product[3],
            'price': product[4],
            'created_at': product[6],
            'last_modified': product[7],
            'category': {
                'category_id': category_id,
                'category_name': category_data[1]
            },
            'stock': {
                'quantity': None,
                'max_stock_quantity': None,
                'unit': None
            }
        }
        
        # Fetch stock information
        oracle_cursor.execute(f"SELECT * FROM stock WHERE product_id = {product[0]}")
        stock_data = oracle_cursor.fetchone()

        if stock_data:
            product_doc['stock']['quantity'] = stock_data[1]
            product_doc['stock']['max_stock_quantity'] = stock_data[2]
            product_doc['stock']['unit'] = stock_data[3]
    
    # Insert the product document into the products collection
    products_collection.insert_one(product_doc)

# Migrate data from Oracle to MongoDB for employees collection
oracle_cursor.execute('SELECT * FROM employees')
employees_data = oracle_cursor.fetchall()

for employee in employees_data:
    department_id = employee[5]
    manager_id = employee[11]
    
    # Fetch department information
    oracle_cursor.execute(f"SELECT * FROM departments WHERE department_id = {department_id}")
    department_data = oracle_cursor.fetchone()
    
    # Create an employee document
    employee_doc = {
        'employee_id': employee[0],
        'first_name': employee[1],
        'middle_name': employee[2],
        'last_name': employee[3],
        'date_of_birth': employee[4],
        'hire_date': employee[6],
        'salary': employee[7],
        'phone_number': employee[8],
        'email': employee[9],
        'ssn_number': employee[10],
        'manager_id': manager_id,
        'department': {
            'department_id': department_id,
            'department_name': department_data[1],
            'manager_id': department_data[2],
            'department_desc': department_data[3]
        },
        'employees_archive': []
    }
    
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
        
        archive_entry_doc = {
            'event_date': archive_entry[0],
            'event_type': archive_entry[1],
            'user_name': archive_entry[2],
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
