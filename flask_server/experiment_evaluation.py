# fair_benchmark_single_file.py
import time
import numpy as np
import pandas as pd
from sklearn.metrics import ndcg_score
from sklearn.metrics.pairwise import cosine_similarity

# load the public data
df = pd.read_csv("fragrance_with_positive.csv")
df["description"] = df["description"].fillna("")
df["positive_rate"] = df["positive_rate"].fillna(0.0)
descriptions = df["description"].tolist()
positive_rate = df["positive_rate"].to_numpy()

# queries & keywords (for static annotation of "whether relevant")
queries = {
    "Sweet girly fragrance": ["sweet", "vanilla", "fruity", "powdery"],
    "Fresh summer fragrance": ["fresh", "green", "citrus", "aqua"],
    "Sexy date fragrance": ["sexy", "musk", "vanilla", "amber"],
    "Unisex woody fragrance": ["woody", "aromatic", "earthy", "green"],
    "Sweet fruity fragrance": ["fruity", "sweet", "candy", "berry"],
    "Sporty and energetic scent": ["fresh", "citrus", "green", "aqua"],
    "Oriental scent for dating": ["amber", "incense", "spicy", "oud"],
    "Woody floral scent": ["woody", "floral", "powdery", "musk"],
    "Campus everyday fragrance": ["fruity", "fresh", "green", "light"],
    "Milky fragrance": ["milky", "sweet", "powdery", "vanilla"],
}

# relevance and metrics
def is_relevant(desc: str, keywords: list[str]) -> int:
    return int(sum(1 for kw in keywords if kw in desc.lower()) >= 2)

def eval_top5(indices: np.ndarray, relevance: np.ndarray):
    if len(indices) == 0:
        return 0.0, 0.0
    top_k = relevance[indices]
    precision = float(top_k.mean())
    ndcg = ndcg_score(
        [relevance],
        [np.isin(np.arange(len(relevance)), indices).astype(int)],
        k=5
    )
    return precision, float(ndcg)

# load the same model + warmup + precalculate the description vector
from bert_model import model as semantic_model 

# warmup (no timing)
_ = semantic_model.encode(descriptions[:32])
_ = semantic_model.encode(["warmup query"])

# calculate the description vector once (reuse, ensure fairness)
desc_embeddings = semantic_model.encode(descriptions)

# three methods (fair timing within a single script)
def run_keyword(query: str, relevance: np.ndarray):
    start = time.perf_counter()
    mask = [query.lower() in d.lower() for d in descriptions]
    idx = np.nonzero(mask)[0][:5]
    cost = time.perf_counter() - start
    p, n = eval_top5(idx, relevance)
    return cost, p, n

def run_semantic(query: str, relevance: np.ndarray):
    start = time.perf_counter()
    q_emb = semantic_model.encode([query])
    scores = cosine_similarity(q_emb, desc_embeddings)[0]
    idx = np.argsort(scores)[-5:][::-1]
    cost = time.perf_counter() - start
    p, n = eval_top5(idx, relevance)
    return cost, p, n

def run_hybrid(query: str, relevance: np.ndarray):
    start = time.perf_counter()
    q_emb = semantic_model.encode([query])
    scores = cosine_similarity(q_emb, desc_embeddings)[0]
    fused = 0.7 * scores + 0.3 * positive_rate
    idx = np.argsort(fused)[-5:][::-1]
    cost = time.perf_counter() - start
    p, n = eval_top5(idx, relevance)
    return cost, p, n

# randomization execution order + result record
rng = np.random.default_rng(20250809) 
methods = [
    ("Keyword Match", run_keyword),
    ("Semantic Match", run_semantic),
    ("Hybrid Recommendation", run_hybrid),
]

results = []
time_records = {name: [] for name, _ in methods}

for query, keywords in queries.items():
    relevance = np.array([is_relevant(desc, keywords) for desc in descriptions], dtype=int)

    # Each query randomizes the execution order of the three methods to avoid the preheating bias caused by the order
    order = np.array(methods, dtype=object)
    rng.shuffle(order)

    for name, fn in order:
        cost, p, n = fn(query, relevance)
        time_records[name].append(cost)
        results.append({
            "Query": query,
            "Method": name,
            "Precision@5": round(p, 2),
            "NDCG@5": round(n, 2)
        })

result_df = pd.DataFrame(results)
avg_times = {method: float(np.mean(times)) for method, times in time_records.items()}

print("\n📊 Evaluation Results for Three Recommendation Methods:\n")
print(result_df.to_markdown(index=False))

print("\n⏱ Average Computing Time (seconds):")
for method, avg_time in avg_times.items():
    print(f"{method}: {avg_time:.6f} s")


result_df.to_csv("recommendation_evaluation_result.csv", index=False)
pd.DataFrame([avg_times]).to_csv("recommendation_avg_time.csv", index=False)




