
import time
import requests
import pandas as pd
import json


test_queries = [
    "I want a long-lasting perfume for girls",
    "Recommend a fresh perfume for men in summer",
    "Suggest a perfume for winter evenings",
    "Looking for a floral scent for women",
    "I need a perfume with good sillage",
    "Unisex fragrance for spring mornings",
    "Something sexy and musky for date night",
    "A perfume that projects strongly and lasts forever"
    "Gender-neutral office-safe scent for daily wear.",
    "All-year-round clean perfume, from day to night.",
    "Not too heavy, lasts a while; good for spring classes.",
    "Beast mode projection for clubbing nights.",
    "Skin-scent only, short wear for interviews.",
    "Fresh citrus for humid summers; doesn’t need to last long.",
    "Date-night musk that fills a room, 24h if possible.",
    "Androgynous vibe, versatile for spring and autumn days.",
    "For anyone, ‘signature’ perfume you can wear year-round.",
    "Gym-safe: clean, close-to-skin, quick to fade.",
    "Summer nights on the beach; must project strongly.",
    "EDT-style freshness for spring mornings.",
    "Warm spicy scent for autumn; office appropriate.",
    "Please no unisex—make it feminine, not too loud.",
    "Make it last forever but keep the trail subtle.",
]


# Define models to test

model_names = ["mistral", "llama2", "gemma", "tinyllama"]


# Format the prompt for structured extraction

def build_prompt(user_query):
    return f"""
You are an intelligent assistant for a perfume recommendation system.
Your task is to extract structured JSON data from the user's natural language query.

You must identify and return the following fields:
- "category": set as "perfume"
- "gender": one of ["male", "female", "unisex"], based on user preference
- "longevity": one of ["moderate", "long lasting", "eternal", "weak", "very weak"]
- "sillage": one of ["intimate", "moderate", "strong", "very strong", "enormous"]
- "suitable_season": list of up to 2 values from ["spring", "summer", "autumn", "winter"]
- "suitable_time": list containing "day", "night", or both

Instructions:
- Use fuzzy matching to recognize synonyms (e.g., "last all day" → "long lasting", "powerful scent trail" → "strong" sillage).
- "last long", "lasts long", "stays long", "lasts all day" → "long lasting"
- "not very long", "soft"→ "weak" "lightly lasts" → "very weak"
- For season and time, identify implicit expressions like “sunny” → “summer”, “evening” → “night”.
- Only return values when confident. Omit uncertain fields.
- Output JSON only, no extra commentary.

Examples:

User input: "Looking for a long-lasting floral perfume with strong projection, best for winter nights"
Response:
{{
  "category": "perfume",
  "longevity": "long lasting",
  "sillage": "strong",
  "suitable_season": ["winter"],
  "suitable_time": ["night"]
}}

User input: "A soft and fresh scent for spring and summer days, preferably for women"
Response:
{{
  "category": "perfume",
  "gender": "female",
  "longevity": "moderate",
  "suitable_season": ["spring", "summer"],
  "suitable_time": ["day"]
}}

Now, the user's input is:
"{user_query}"

Please return only the JSON format, without any additional text:
"""


# Function to query Ollama model and measure response time

def query_model(model, user_query):
    prompt = build_prompt(user_query)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    start_time = time.perf_counter()
    response = requests.post("http://localhost:11434/api/generate", json=payload)
    end_time = time.perf_counter()

    duration = round(end_time - start_time, 3)
    try:
        raw_output = response.json().get("response", "").strip()
        structured = json.loads(raw_output)
    except Exception as e:
        structured = None

    return raw_output, duration, structured


# Run comparison and store results

records = []

for model in model_names:
    print(f"\n🔍 Testing model: {model}")
    for query in test_queries:
        print(f"🧪 Query: {query}")
        output_text, duration, parsed = query_model(model, query)

        records.append({
            "model": model,
            "query": query,
            "response": output_text,
            "parsed_json": parsed,
            "time_sec": duration
        })


# Save result to CSV

df = pd.DataFrame(records)
df.to_csv("model_comparison_results.csv", index=False)
print("✅ Comparison completed. Results saved to 'model_comparison_results.csv'")
