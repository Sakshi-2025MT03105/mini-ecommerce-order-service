
import sqlite3

def get_db_connection():
    connection = sqlite3.connect('orders.db')
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_db_connection()

    connection.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    connection.commit()
    connection.close()
