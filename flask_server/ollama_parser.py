import requests
from preprocess_query import preprocess_query

# Define local Ollama API endpoint 
OLLAMA_LOCAL_ENDPOINT = "http://localhost:11434/api/generate"

def parse_user_query(user_query):
    """Use Ollama to parse the user's query and return structured JSON"""
    user_query = preprocess_query(user_query)

    # ✅ Prompt to extract all relevant perfume fields
    prompt = f"""
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

    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }

    # Send POST request to Ollama
    response = requests.post(OLLAMA_LOCAL_ENDPOINT, json=payload)

    if response.status_code == 200:
        try:
            raw_text = response.json()["response"]
            print("🔹 Ollama response:", raw_text)

            # Extract JSON portion
            json_start = raw_text.find("{")
            json_end = raw_text.rfind("}") + 1
            cleaned_json = raw_text[json_start:json_end].replace("null", "None")

            parsed = eval(cleaned_json)

            # Set defaults for missing fields
            DEFAULT_QUERY = {
                "category": "perfume",
                "gender": None,
                "longevity": None,
                "sillage": None,
                "suitable_season": None,
                "suitable_time": None
            }

            for k in DEFAULT_QUERY:
                parsed.setdefault(k, DEFAULT_QUERY[k])

            print("✅ Parsed JSON:", parsed)
            return parsed

        except Exception as e:
            print("❌ JSON parsing failed:", str(e))
            return None
    else:
        print("❌ Ollama API error:", response.text)
        return None


if __name__ == "__main__":
    # Example test cases
    test_queries = [
        "I want a fresh floral perfume for summer that lasts long.",
        "Looking for a masculine scent for night use in winter.",
        "Give me a unisex perfume with woody and spicy notes.",
  
    ]

    for q in test_queries:
        print(f"\n🧪 Input: {q}")
        result = parse_user_query(q)
        print("Parsed JSON:", result)


