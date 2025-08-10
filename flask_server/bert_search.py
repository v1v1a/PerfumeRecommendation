from flask import Blueprint, request, jsonify
from sqlalchemy import text
from server_config import db
from bert_similarity import compute_similarity
from ollama_parser import parse_user_query

# Define the blueprint for BERT-based search
bert_search_bp = Blueprint("bert_search", __name__)

# Function to dynamically construct SQL query based on parsed conditions
def build_dynamic_sql(parsed_query):
    base_sql = "SELECT id, name, description FROM products WHERE 1=1"
    conditions = []
    params = {}

    # main_accords
    if parsed_query.get("main_accords"):
        conditions.append(" AND (" + " OR ".join(
            [f"main_accords LIKE :accord_{i}" for i in range(len(parsed_query["main_accords"]))]) + ")"
        )
        for i, accord in enumerate(parsed_query["main_accords"]):
            params[f"accord_{i}"] = f"%{accord.lower()}%"

    # gender
    if parsed_query.get("gender"):
        conditions.append(" AND LOWER(gender) = :gender")
        params["gender"] = parsed_query["gender"].lower()

    # suitable_season
    if parsed_query.get("suitable_season"):
        season_list = parsed_query["suitable_season"]
        if isinstance(season_list, list):
            season_clauses = []
            for i, season in enumerate(season_list):
                key = f"season_{i}"
                season_clauses.append(f"LOWER(suitable_season) LIKE :{key}")
                params[key] = f"%{season.lower()}%"
            conditions.append(" AND (" + " OR ".join(season_clauses) + ")")

    # suitable_time
    if parsed_query.get("suitable_time"):
        time_list = parsed_query["suitable_time"]
        if isinstance(time_list, list):
            time_clauses = []
            for i, t in enumerate(time_list):
                key = f"time_{i}"
                time_clauses.append(f"LOWER(suitable_time) LIKE :{key}")
                params[key] = f"%{t.lower()}%"
            conditions.append(" AND (" + " OR ".join(time_clauses) + ")")

    if parsed_query.get("longevity") and parsed_query["longevity"] != "undefined":
        conditions.append(" AND LOWER(longevity) LIKE :longevity")
        params["longevity"] = f"%{parsed_query['longevity'].lower()}%"

    if parsed_query.get("sillage") and parsed_query["sillage"] != "undefined":
        conditions.append(" AND LOWER(sillage) LIKE :sillage")
        params["sillage"] = f"%{parsed_query['sillage'].lower()}%"
    

    final_sql = base_sql + "".join(conditions)
    return final_sql, params

# Main route for BERT-based semantic search
@bert_search_bp.route('/search_by_bert', methods=['POST'])
def search_by_bert():
    data = request.json
    user_query = data.get("query", "")
    print("🧪 Raw user query:", user_query)

    # Parse structured information from the user query using a language model
    parsed_query = parse_user_query(user_query)
    print("🧠 Parsed structured query:", parsed_query)

    if not parsed_query:
        return jsonify({"error": "Failed to parse query"}), 400

    # Dynamically build SQL query from structured fields
    sql, params = build_dynamic_sql(parsed_query)
    print("Constructed SQL:", sql)
    print("SQL parameters:", params)

    result = db.session.execute(text(sql), params)

    products = [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2]
        }
        for row in result
    ]

    print(f"🎯 Number of matched products: {len(products)}")
    for p in products:
        print("➡️ Product:", p["name"])

    if not products:
        return jsonify([])

    # Compute semantic similarity between query and product descriptions
    results = compute_similarity(user_query, products)
    print("🔍 Top 5 similarity-based recommendations:")
    for r in results:
        print(f"{r['name']} - Score: {r['final_score']:.3f}")

    return jsonify(results)





