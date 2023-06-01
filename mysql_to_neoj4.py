from neo4j import GraphDatabase
import mysql.connector
from tqdm import tqdm
import time

# Função para criar o grafo no Neo4j
def create_graph(tx, data):
    # Criar nós User
    for user in tqdm(data['users'], desc='Creating User nodes'):
        tx.run("CREATE (:User {user_id: $user_id, first_name: $first_name, middle_name: $middle_name, last_name: $last_name, phone_number: $phone_number, email: $email, username: $username, user_password: $user_password, registered_at: $registered_at})",
               user_id=user['user_id'], first_name=user['first_name'], middle_name=user['middle_name'],
               last_name=user['last_name'], phone_number=user['phone_number'], email=user['email'],
               username=user['username'], user_password=user['user_password'], registered_at=user['registered_at'])

    # Criar nós Session
    for session in tqdm(data['sessions'], desc='Creating Session nodes'):
        tx.run("CREATE (:Session {session_id: $session_id, created_at: $created_at, modified_at: $modified_at})",
               session_id=session['session_id'], created_at=session['created_at'], modified_at=session['modified_at'])

    # Criar relacionamento HAS_SESSION entre User e Session
    for user in tqdm(data['sessions'], desc='Creating HAS_SESSION relationships'):
        tx.run("MATCH (u:User {user_id: $user_id}), (s:Session {session_id: $session_id}) CREATE (u)-[:HAS_SESSION]->(s)",
               user_id=user['user_id'], session_id=user['session_id'])

    # Criar nós Cart
    for cart in tqdm(data['carts'], desc='Creating Cart nodes'):
        tx.run("CREATE (:Cart {cart_id: $cart_id, product_id: $product_id, quantity: $quantity, created_at: $created_at, modified_at: $modified_at})",
               cart_id=cart['cart_item_id'], product_id=cart['product_id'], quantity=cart['quantity'], created_at=cart['created_at'], modified_at=cart['modified_at'])

    # Criar relacionamento HAS_CART entre Session e Cart
    for cart in tqdm(data['carts'], desc='Creating HAS_CART relationships'):
              tx.run("MATCH (s:Session {session_id: $session_id}), (c:Cart {cart_id: $cart_id}) CREATE (s)-[:HAS_CART]->(c)",
                     session_id=cart['session_id'], cart_id=cart['cart_item_id'])

    # Criar nós Address
    # TODO: Alterar o nome para "address_id", quando a tabela do MySQL for alterada
    for address in tqdm (data['addresses'], desc='Creating Address nodes'):
        tx.run("CREATE (:Address {address_id: $address_id, line_1: $line_1, line_2: $line_2, city: $city, zip_code: $zip_code, province: $province, country: $country})",
               address_id=address['adress_id'], line_1=address['line_1'], line_2=address['line_2'],
               city=address['city'], zip_code=address['zip_code'], province=address['province'], country=address['country'])
        
    # Criar nós Product
    for product in tqdm(data['products'], desc='Creating Product nodes'):
        tx.run("CREATE (:Product {product_id: $product_id, product_name: $product_name, sku: $sku, price: $price, created_at: $created_at, last_modified: $last_modified, category_id: $category_id, discount_id: $discount_id})",
               product_id=product['product_id'], product_name=product['product_name'], sku=product['sku'],
               price=product['price'], created_at=product['created_at'], last_modified=product['last_modified'],
               category_id=product['category_id'], discount_id=product['discount_id'])

    # Criar nós Category
    for category in tqdm(data['categories'], desc='Creating Category nodes'):
        tx.run("CREATE (:Category {category_id: $category_id, category_name: $category_name})",
               category_id=category['category_id'], category_name=category['category_name'])

    # Criar relacionamento BELONGS_TO entre Product e Category
    for product in tqdm (data['products'], desc='Creating BELONGS_TO relationships'):
        tx.run("MATCH (p:Product {product_id: $product_id}), (c:Category {category_id: $category_id}) CREATE (p)-[:BELONGS_TO]->(c)",
               product_id=product['product_id'], category_id=product['category_id'])

    # Criar nós Discount
    for discount in tqdm(data['discounts'], desc='Creating Discount nodes'):
        tx.run("CREATE (:Discount {discount_id: $discount_id, discount_name: $discount_name, discount_desc: $discount_desc, discount_percent: $discount_percent, is_active_status: $is_active_status, created_at: $created_at, modified_at: $modified_at})",
               discount_id=discount['discount_id'], discount_name=discount['discount_name'], discount_desc=discount['discount_desc'],
               discount_percent=discount['discount_percent'], is_active_status=discount['is_active_status'],
               created_at=discount['created_at'], modified_at=discount['modified_at'])

    # Criar relacionamento HAS_DISCOUNT entre Product e Discount
    for product in tqdm(data['products'], desc='Creating HAS_DISCOUNT relationships'):
        tx.run("MATCH (p:Product {product_id: $product_id}), (d:Discount {discount_id: $discount_id}) CREATE (p)-[:HAS_DISCOUNT]->(d)",
               product_id=product['product_id'], discount_id=product['discount_id'])

    # Criar nós Payment
    for payment in tqdm(data['payments'], desc='Creating Payment nodes'):
        tx.run("CREATE (:Payment {payment_id: $payment_id, amount: $amount, provider: $provider, payment_status: $payment_status, created_at: $created_at, modified_at: $modified_at})",
               payment_id=payment['payment_details_id'], amount=payment['amount'], provider=payment['provider'],
               payment_status=payment['payment_status'], created_at=payment['created_at'], modified_at=payment['modified_at'])

    # Criar nós Employee
    for employee in tqdm(data['employees'], desc='Creating Employee nodes'):
        tx.run("CREATE (:Employee {employee_id: $employee_id, first_name: $first_name, middle_name: $middle_name, last_name: $last_name, date_of_birth: $date_of_birth, hire_date: $hire_date, salary: $salary, phone_number: $phone_number, email: $email, ssn_number: $ssn_number, manager_id: $manager_id})",
               employee_id=employee['employee_id'], first_name=employee['first_name'], middle_name=employee['middle_name'],
               last_name=employee['last_name'], date_of_birth=employee['date_of_birth'], hire_date=employee['hire_date'],
               salary=employee['salary'], phone_number=employee['phone_number'], email=employee['email'],
               ssn_number=employee['ssn_number'], manager_id=employee['manager_id'])

    # Criar nós Department
    for department in tqdm(data['departments'], desc='Creating Department nodes'):
        tx.run("CREATE (:Department {department_id: $department_id, department_name: $department_name, department_desc: $department_desc})",
               department_id=department['department_id'], department_name=department['department_name'], department_desc=department['department_desc'])

    # Criar relacionamento BELONGS_TO entre Employee e Department
    for employee in tqdm(data['employees'], desc='Creating BELONGS_TO relationships'):
        tx.run("MATCH (e:Employee {employee_id: $employee_id}), (d:Department {department_id: $department_id}) CREATE (e)-[:BELONGS_TO]->(d)",
               employee_id=employee['employee_id'], department_id=employee['department_id'])

    # Criar relacionamento MANAGES entre Employee e Employee
    for employee in tqdm(data['employees'], desc='Creating MANAGES relationships'):
        if employee['manager_id']:
            tx.run("MATCH (e1:Employee {employee_id: $employee_id1}), (e2:Employee {employee_id: $employee_id2}) CREATE (e1)-[:MANAGES]->(e2)",
                   employee_id1=employee['manager_id'], employee_id2=employee['employee_id'])

    # Criar nós Stock
    for stock in tqdm(data['stock'], desc='Creating Stock nodes'):
        tx.run("CREATE (:Stock {quantity: $quantity, max_stock_quantity: $max_stock_quantity, unit: $unit})",
               quantity=stock['quantity'], max_stock_quantity=stock['max_stock_quantity'], unit=stock['unit'])

    # Criar relacionamento HAS_STOCK entre Product e Stock
    for product in tqdm(data['products'], desc='Creating HAS_STOCK relationships'):
        product_id = product['product_id']
        tx.run("MATCH (p:Product {product_id: $product_id}), (s:Stock {product_id: $product_id}) "
               "CREATE (p)-[:HAS_STOCK]->(s)",
               product_id=product_id)
        
    # TODO: Associar cada Cart ao produto correspondente (Category -> Product <- Cart)
    for cart in tqdm(data['carts'], desc='Creating HAS_PRODUCT relationships'):
        tx.run("MATCH (c:Cart {cart_id: $cart_id}), (p:Product {product_id: $product_id}) "
                   "CREATE (c)-[:HAS_PRODUCT]->(p)",
                   cart_id=cart['cart_item_id'], product_id=cart['product_id'])
    
    # TODO: Criar nós Order
    for order in tqdm(data['order_items'], desc='Creating Order nodes'):
        tx.run(            """
            CREATE (o:Order {
                order_items_id: $order_items_id,
                order_details_id: $order_details_id,
                product_id: $product_id,
                created_at: $created_at,
                modified_at: $modified_at
            })
            """,
            order_items_id=order['order_items_id'],
            order_details_id=order['order_details_id'],
            product_id=order['product_id'],
            created_at=order['created_at'],
            modified_at=order['modified_at']
        )

     # TODO: Criar nós OrderDetails e atribuir ao respectivo Order (Order -[HAS_DETAILS]-> OrderDetails) E (OrderDetails -[PAYED_BY]-> Payment)
    for order in tqdm(data['order_details'], desc='Creating OrderDetails nodes'):
        tx.run("CREATE (:OrderDetails {order_details_id: $order_details_id, user_id: $user_id, total: $total, payment_id: $payment_id, shipping_method: $shipping_method, delivery_adress_id: $delivery_adress_id, created_at: $created_at, modified_at: $modified_at})",
               order_details_id=order['order_details_id'], user_id=order['user_id'], total=order['total'], payment_id=order['payment_id'],
               shipping_method=order['shipping_method'], delivery_adress_id=order['delivery_adress_id'], created_at=order['created_at'], modified_at=order['modified_at'])
        # Associar aos payments11
        tx.run("MATCH (od:OrderDetails {order_details_id: $order_details_id}), (p:Payment {payment_id: $payment_id}) "
                "CREATE (od)-[:PAYED_WITH]->(p)",
                order_details_id=order['order_details_id'], payment_id=order['payment_id'])

    # TODO: Associar User ao seu OrderDetails
    for order in tqdm(data['order_details'], desc='Creating PLACED_ORDER relationships'):
        tx.run("MATCH (u:User {user_id: $user_id}), (o:Order {order_details_id: $order_details_id}) "
               "CREATE (u)-[:PLACED_ORDER]->(o)",
               user_id=order['user_id'], order_details_id=order['order_details_id'])
        
    # TODO: Através dos nodos OrderDetails, determinar o Order e associar esse Order ao User que o fez através da relação PLACED_ORDER
    # MATCH (od:OrderDetails)-[:PLACED_ORDER]->(o:Order)
    # WITH od, o
    # MATCH (u:User)-[:PLACED_ORDER]->(o)
    # MERGE (u)-[:PLACED_ORDER]->(o)
    # Percorrer cada order_item
    for order_item in tqdm(data['order_items'], desc='Creating PLACED_ORDER relationships'):
        order_details_id = order_item['order_details_id']
    
        # Consultar o OrderDetails correspondente
        order_details = tx.run(
            "MATCH (od:OrderDetails) WHERE od.order_details_id = $order_details_id RETURN od",
            order_details_id=order_details_id
        ).single()
    
        if order_details:
            order = order_details['od']['order']
            user = order_details['od']['user']

            # Associar o Order ao User através da relação PLACED_ORDER
            tx.run(
                "MATCH (o:Order), (u:User) WHERE o.order = $order AND u.user = $user "
                "MERGE (u)-[:PLACED_ORDER]->(o)",
                order=order, user=user
            )

    # TODO: Associar OrderDetails aos nós Order_items
    for order in tqdm(data['order_details'], desc='Creating HAS_DETAILS relationships'):
        tx.run("MATCH (od:OrderDetails {order_details_id: $order_details_id}), (o:Order) "
               "WHERE o.order_details_id = $order_details_id "
               "CREATE (o)-[:HAS_DETAILS]->(od)",
               order_details_id=order['order_details_id'])
        
    # TODO: Associar Address aos OrderDetails
    for order in tqdm(data['order_details'], desc='Creating DELIVERED_TO relationships'):
        address_id = order['delivery_adress_id']
        order_details_id = order['order_details_id']

        tx.run("MATCH (a:Address), (od:OrderDetails) "
               "WHERE a.address_id = $address_id AND od.order_details_id = $order_details_id "
               "CREATE (od)-[:DELIVERED_TO]->(a)",
               address_id=address_id, order_details_id=order_details_id)

    # TODO: Associar produtos aos Order_items respetivo
    for order_item in tqdm(data['order_items'], desc='Creating CONTAINS_PRODUCT relationships'):
        order_item_id = order_item['order_items_id']
        product_id = order_item['product_id']

        # Verificar se já existe uma relação entre o Order_item e o produto
        existing_relationship = tx.run(
            "MATCH (oi:Order)-[:CONTAINS_PRODUCT]->(p:Product) "
            "WHERE oi.order_items_id = $order_item_id AND p.product_id = $product_id "
            "RETURN oi, p",
            order_item_id=order_item_id,
            product_id=product_id
        ).single()

        if existing_relationship:
            continue

        # Associar o produto ao Order_item
        tx.run("MATCH (o:Order {order_details_id: $order_details_id}), (p:Product {product_id: $product_id}) "
               "CREATE (o)-[:CONTAINS_PRODUCT]->(p)",
               order_details_id=order_item['order_details_id'],
               product_id=order_item['product_id'])

    # TODO: tratar os archives
    # Criar nós EmployeeArchive
    for archive in tqdm(data['archives'], desc='Creating EmployeeArchive nodes'):
        tx.run("CREATE (:EmployeeArchive {event_date: $event_date, event_type: $event_type, user_name: $user_name, old_employee_id: $old_employee_id, old_first_name: $old_first_name, old_middle_name: $old_middle_name, old_last_name: $old_last_name, old_date_of_birth: $old_date_of_birth, old_department_id: $old_department_id, old_hire_date: $old_hire_date, old_salary: $old_salary, old_phone_number: $old_phone_number, old_email: $old_email, old_ssn_number: $old_ssn_number, old_manager_id: $old_manager_id, new_employee_id: $new_employee_id, new_first_name: $new_first_name, new_middle_name: $new_middle_name, new_last_name: $new_last_name, new_date_of_birth: $new_date_of_birth, new_department_id: $new_department_id, new_hire_date: $new_hire_date, new_salary: $new_salary, new_phone_number: $new_phone_number, new_email: $new_email, new_ssn_number: $new_ssn_number, new_manager_id: $new_manager_id})",
                event_date=archive['event_date'], event_type=archive['event_type'], user_name=archive['user_name'], old_employee_id=archive['old_employee_id'], old_first_name=archive['old_first_name'], old_middle_name=archive['old_middle_name'], old_last_name=archive['old_last_name'], old_date_of_birth=archive['old_date_of_birth'], old_department_id=archive['old_department_id'], old_hire_date=archive['old_hire_date'], old_salary=archive['old_salary'], old_phone_number=archive['old_phone_number'], old_email=archive['old_email'], old_ssn_number=archive['old_ssn_number'], old_manager_id=archive['old_manager_id'], new_employee_id=archive['new_employee_id'], new_first_name=archive['new_first_name'], new_middle_name=archive['new_middle_name'], new_last_name=archive['new_last_name'], new_date_of_birth=archive['new_date_of_birth'], new_department_id=archive['new_department_id'], new_hire_date=archive['new_hire_date'], new_salary=archive['new_salary'], new_phone_number=archive['new_phone_number'], new_email=archive['new_email'], new_ssn_number=archive['new_ssn_number'], new_manager_id=archive['new_manager_id'])

     # TODO: Criar relacionamento LIVES_AT entre nodos Address e users (usar o campo adress_id da tabela order_details)
    for order in tqdm(data['order_details'], desc='Creating LIVES_AT relationships'):
        address_id = order['delivery_adress_id']
        user_id = order['user_id']

        tx.run("MATCH (a:Address {address_id: $address_id}), (u:User {user_id: $user_id}) "
               "CREATE (u)-[:LIVES_AT]->(a)",
               address_id=address_id, user_id=user_id)

# Conexão com o MySQL
mysql_connection = mysql.connector.connect(
    host="35.188.76.19",
    user="purp",
    password="purp",
    database="tp_nosql",
    port=3306
)

# Obter dados do MySQL
# Cerificar se a conexão foi estabelecida
if mysql_connection.is_connected():
    print('Connected to MySQL database.')
    cursor = mysql_connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM store_users")
    users = cursor.fetchall()
    cursor.execute("SELECT * FROM product")
    products = cursor.fetchall()
    cursor.execute("SELECT * FROM product_categories")
    categories = cursor.fetchall()
    cursor.execute("SELECT * FROM discount")
    discounts = cursor.fetchall()
    cursor.execute("SELECT * FROM shopping_session")
    sessions = cursor.fetchall()
    cursor.execute("SELECT * FROM cart_item")
    carts = cursor.fetchall()
    cursor.execute("SELECT * FROM order_details")
    order_details = cursor.fetchall()
    cursor.execute("SELECT * FROM addresses")
    addresses = cursor.fetchall()
    cursor.execute("SELECT * FROM payment_details")
    payments = cursor.fetchall()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()
    cursor.execute("SELECT * FROM stock")
    stock = cursor.fetchall()
    cursor.execute("SELECT * FROM order_items")
    order_items = cursor.fetchall()
    cursor.execute("SELECT * FROM employees_archive")
    archives = cursor.fetchall()
    cursor.close()
mysql_connection.close()

# Conexão com o Neo4j
neo4j_uri = "neo4j+s://970e1e32.databases.neo4j.io"
neo4j_user = "neo4j"
neo4j_password = "tjB1n2AHzPLzbvTlPb4LnWz767gWkvoxZu1mfR1g_-o"
neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# Criar base de dados no Neo4j
with neo4j_driver.session() as session:
    # Verificar se a sessão foi estabelecida
    if session is None:
        print("Neo4j connection failed.")
        exit(-1)

    print("Neo4j connection established successfully.")
    # Delete all nodes and relationships
    print("Deleting all previous nodes and relationships...")
    session.run("MATCH (n) DETACH DELETE n")

    # Create graph
    print("Creating the graph...")
    session.execute_write(create_graph, {
        'users': users,
        'products': products,
        'categories': categories,
        'discounts': discounts,
        'sessions': sessions,
        'carts': carts,
        'order_details': order_details,
        'addresses': addresses,
        'payments': payments,
        'employees': employees,
        'departments': departments,
        'stock': stock,
        'order_items': order_items,
        'archives': archives,
    })

print("Neo4j database created successfully.")

# Fechar conexão com o Neo4j
neo4j_driver.close()
