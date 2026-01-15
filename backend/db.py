# Import MySQL connector library
import mysql.connector

# Function to create and return a database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",        # MySQL server address
        user="root",             # MySQL username
        password="sanju14",# 🔴 replace with your root password
        database="petcare_db"    # Database name
    )
