from flask import Flask, request, jsonify
from flask_cors import CORS

# use relative import (no need to write flask_server prefix)
from server_config import app
from product_search import product_search_bp
from bert_search import bert_search_bp


CORS(app)


app.register_blueprint(product_search_bp)
app.register_blueprint(bert_search_bp)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8900, debug=True)



