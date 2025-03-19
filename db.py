import mysql.connector

# Function to connect to the MySQL database
def get_db_connection():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pythonflask",  # Use the pythonflask database
        port=3305
    )
    return mydb