import cx_Oracle
from py2neo import Graph

# Connect to Oracle
oracle_conn = cx_Oracle.connect(user="uminho", password="uminho2020", dsn="localhost:1521/xe")
oracle_cursor = oracle_conn.cursor()

# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

# Migrate data from Oracle to Neo4j for users
oracle_cursor.execute('SELECT * FROM store_users')
users_data = oracle_cursor.fetchall()

for user in users_data:
    user_id = user['user_id']
    
    # Create user node
    graph.run(
        '''
        MERGE (u:User {user_id: $user_id})
        SET u += {
            first_name: $first_name,
            middle_name: $middle_name,
            last_name: $last_name,
            phone_number: $phone_number,
            email: $email,
            username: $username,
            user_password: $user_password,
            registered_at: $registered_at
        }
        ''',
        user_id=user_id,
        first_name=user['first_name'],
        middle_name=user['middle_name'],
        last_name=user['last_name'],
        phone_number=user['phone_number'],
        email=user['email'],
        username=user['username'],
        user_password=user['user_password'],
        registered_at=user['registered_at']
    )

    # Create shopping session relationships
    oracle_cursor.execute(f"SELECT * FROM shopping_session WHERE user_id = {user_id}")
    sessions_data = oracle_cursor.fetchall()

    for session in sessions_data:
        session_id = session['session_id']

        # Create session node
        graph.run(
            '''
            MERGE (s:Session {session_id: $session_id})
            SET s += {
                created_at: $created_at,
                modified_at: $modified_at
            }
            ''',
            session_id=session_id,
            created_at=session['created_at'],
            modified_at=session['modified_at']
        )

        # Create relationship between user and session
        graph.run(
            '''
            MATCH (u:User {user_id: $user_id}), (s:Session {session_id: $session_id})
            MERGE (u)-[:HAS_SESSION]->(s)
            ''',
            user_id=user_id,
            session_id=session_id
        )

        # Create cart item relationships
        oracle_cursor.execute(f"SELECT * FROM cart_item WHERE session_id = {session_id}")
        cart_items_data = oracle_cursor.fetchall()

        for cart_item in cart_items_data:
            product_id = cart_item['product_id']

            # Create cart item node
            graph.run(
                '''
                MERGE (ci:CartItem {product_id: $product_id, session_id: $session_id})
                SET ci += {
                    quantity: $quantity,
                    created_at: $created_at,
                    modified_at: $modified_at
                }
                ''',
                product_id=product_id,
                session_id=session_id,
                quantity=cart_item['quantity'],
                created_at=cart_item['created_at'],
                modified_at=cart_item['modified_at']
            )

            # Create relationship between session and cart item
            graph.run(
                '''
                MATCH (s:Session {session_id: $session_id}), (ci:CartItem {product_id: $product_id, session_id: $session_id})
                MERGE (s)-[:HAS_CART_ITEM]->(ci)
                ''',
                session_id=session_id,
                product_id=product_id
            )

# Migrate data from Oracle to Neo4j for products
oracle_cursor.execute('SELECT * FROM product')
products_data = oracle_cursor.fetchall()

for product in products_data:
    category_id = product['category_id']
    discount_id = product['discount_id']

    # Create product node
    graph.run(
        '''
        MERGE (p:Product {product_id: $product_id})
        SET p += {
            product_name: $product_name,
            sku: $sku,
            price: $price,
            created_at: $created_at,
            last_modified: $last_modified
        }
        ''',
        product_id=product['product_id'],
        product_name=product['product_name'],
        sku=product['sku'],
        price=product['price'],
        created_at=product['created_at'],
        last_modified=product['last_modified']
    )

    # Create relationship between product and category
    oracle_cursor.execute(f"SELECT * FROM product_categories WHERE category_id = {category_id}")
    category_data = oracle_cursor.fetchone()

    graph.run(
        '''
        MATCH (p:Product {product_id: $product_id}), (c:Category {category_id: $category_id})
        MERGE (p)-[:BELONGS_TO_CATEGORY]->(c)
        ''',
        product_id=product['product_id'],
        category_id=category_id
    )

    if discount_id is not None:
        # Create relationship between product and discount
        oracle_cursor.execute(f"SELECT * FROM discount WHERE discount_id = {discount_id}")
        discount_data = oracle_cursor.fetchone()

        graph.run(
            '''
            MATCH (p:Product {product_id: $product_id}), (d:Discount {discount_id: $discount_id})
            MERGE (p)-[:HAS_DISCOUNT]->(d)
            ''',
            product_id=product['product_id'],
            discount_id=discount_id
        )

# Close the Oracle cursor and connection
oracle_cursor.close()
oracle_conn.close()
