
from flask import Flask, jsonify, request
import sqlite3
import requests

from database import get_db_connection, create_table

app = Flask(__name__)

# Create the orders table when the service starts
create_table()


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "success",
        "message": "Order Service is running"
    }), 200



@app.route('/orders', methods=['POST'])
def place_order():

    data = request.get_json()

    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not isinstance(product_id, int) or product_id <= 0:
        return jsonify({"message": "Valid product_id is required"}), 400

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"message": "Valid positive quantity is required"}), 400

    try:
        # Get product details from Product Service
        response = requests.get(
            f'http://127.0.0.1:5001/products/{product_id}',
            timeout=5
        )

    except requests.exceptions.RequestException:
        return jsonify({
            "message": "Product Service is unavailable"
        }), 503

    if response.status_code == 404:
        return jsonify({"message": "Product not found"}), 404

    if response.status_code != 200:
        return jsonify({"message": "Unable to retrieve product details"}), 502

    product = response.json()

    if quantity > product['stock']:
        return jsonify({
            "message": "Insufficient stock",
            "available_stock": product['stock']
        }), 400

    product_name = product['name']
    unit_price = product['price']
    total_price = quantity * unit_price

    connection = get_db_connection()

    cursor = connection.execute('''
        INSERT INTO orders
        (product_id, product_name, quantity, unit_price, total_price)
        VALUES (?, ?, ?, ?, ?)
    ''', (product_id, product_name, quantity, unit_price, total_price))

    order_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Order placed successfully",
        "order_id": order_id,
        "product_name": product_name,
        "quantity": quantity,
        "unit_price": unit_price,
        "total_price": total_price
    }), 201

# GET All Orders

@app.route('/orders', methods=['GET'])
def get_all_orders():

    connection = get_db_connection()

    orders = connection.execute(
        'SELECT * FROM orders'
    ).fetchall()

    connection.close()

    orders_list = []

    for order in orders:
        orders_list.append(dict(order))

    return jsonify(orders_list), 200


# GET by ORDER ID


@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id):

    connection = get_db_connection()

    order = connection.execute(
        'SELECT * FROM orders WHERE id = ?',
        (order_id,)
    ).fetchone()

    connection.close()

    if order is None:
        return jsonify({
            "message": "Order not found"
        }), 404

    return jsonify(dict(order)), 200




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
