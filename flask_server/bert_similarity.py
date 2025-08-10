from sentence_transformers import util
from bert_model import model

def compute_similarity(user_query, products):
    """
    Calculate the BERT similarity between the input user_query and all product descriptions
    Superimpose positive_rate, sort and return Top 5.
    """

    user_embedding = model.encode([user_query], convert_to_tensor=True)


    product_descriptions = [p["description"] for p in products]
    product_embeddings = model.encode(product_descriptions, convert_to_tensor=True)


    cosine_scores = util.cos_sim(user_embedding, product_embeddings)[0]


    results = []
    for product, score in zip(products, cosine_scores):
        similarity = float(score)
        positive_rate = product.get("positive_rate", 0)
        final_score = similarity * 0.7 + positive_rate * 0.3

        results.append({
            "id": product["id"],
            "name": product["name"],
            "description": product["description"],
            "similarity": similarity,
            "final_score": final_score
        })

    # Sort by final_score and take the top 5
    results = sorted(results, key=lambda x: x["final_score"], reverse=True)[:5]

    return results
