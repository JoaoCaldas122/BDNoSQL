from pymongo import MongoClient

# Connect to MongoDB
url = "Acrescenta"

mongo_client = MongoClient(url)
mongo_db = mongo_client['tpnosql']
users_collection = mongo_db['users']
products_collection = mongo_db['products']
employees_collection = mongo_db['employees']

min_total = 1000

query = {
    'orders': {
        '$elemMatch': {
            'total': {'$gt': min_total}
        }
    }
}

print("Tem ordens com valor superior a 1000")
result = users_collection.find(query)
for user in result:
    print(f'{user["first_name"]} {user["last_name"]}')
    for order in user['orders']:
        if order['total'] > 1000:
            print(f'Order ID: {order["order_details_id"]}')
            #print(f'Total: {order["total"]}')
    print('===========')
print('\n\n')

print("Artigos com desconto ativo")
query = {
    'discount.is_active_status': "Y"
}

result = products_collection.find(query)
for product in result:
    print(f'{product["product_name"]} - {product["price"]}€')
print('\n\n')

print("Todos os trabalhadores que trabalham no departamento Development.")
# Consulta
query = {
    'department.department_name': "Development"
}

result = employees_collection.find(query)
for employee in result:
    print(f'{employee["first_name"]} {employee["last_name"]} - {employee["salary"]}€')

print('\n\n')

print("Produtos disponíveis na categoria TV and Video")

# Consulta
query = {
    'category.category_name': "TV and Video",
    'stock.quantity': {'$gt': 0}
}

result = products_collection.find(query)
for product in result:
    print(f'{product["product_name"]} - {product["price"]}€')

print('\n\n')

print('Recuperar todos os usuários que fizeram uma compra nos últimos 365 dias')

from datetime import datetime, timedelta

# Defina a data de referência (hoje)
reference_date = datetime.now()

# Calcule a data há 7 dias atrás
start_date = reference_date - timedelta(days=365)

# Consulta
query = {
    'sessions': {
        '$elemMatch': {
            'created_at': {'$gte': start_date}
        }
    }
}

result = users_collection.find(query)
for user in result:
    print(f'{user["first_name"]} {user["last_name"]}')
