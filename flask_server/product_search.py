from flask import Blueprint, request, jsonify
from sqlalchemy import text
from server_config import db

# Define the Blueprint
product_search_bp = Blueprint("product_search", __name__)

# Function to query products from the database
def search_products_in_db(category, max_price):
    """Query products from the database based on category and price"""
    sql = "SELECT * FROM products WHERE description LIKE :category"
    params = {"category": f"%{category}%"}

    if max_price is not None:
        sql += " AND price <= :max_price"
        params["max_price"] = max_price

    try:
        result = db.session.execute(text(sql), params)
        products = [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": row[3] if len(row) > 3 else None
            }
            for row in result
        ]
        return products
    except Exception as e:
        print("Database query failed:", str(e))
        return []

# Define API route
@product_search_bp.route("/search_products", methods=["POST"])
def search_products():
    """
    Example frontend POST request: {"category": "sweet", "max_price": 200}
    Returns a list of matched products
    """
    data = request.json
    category = data.get("category", "")
    max_price = data.get("max_price")

    products = search_products_in_db(category, max_price)
    return jsonify(products)


