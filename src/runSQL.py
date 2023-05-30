#pip install mysql-connector-python
import mysql.connector

# Set the configuration for your MySQL connection
config = {
    'user': 'root',
    'password': 'password',
    'host': '34.79.29.158',
    'database': '',
    'raise_on_warnings': True
}

# Connect to the MySQL server
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# Execute the SQL commands from the database.sql file
with open('1-database.sql', 'r') as file:
    sql_commands = file.read()

for result in cursor.execute(sql_commands, multi=True):
    pass

# Execute the SQL commands from the scripts.sql file
with open('2-scripts.sql', 'r') as file:
    sql_commands = file.read()

for result in cursor.execute(sql_commands, multi=True):
    pass

# Close the cursor and the connection
cursor.close()
cnx.close()
