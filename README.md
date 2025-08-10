This project is a **perfume recommendation system** that supports natural language queries, keyword matching, BERT semantic matching, and hybrid recommendations (semantic similarity + sentiment score + structured filtering).  
The frontend is built with **React** (in `client/`), and the backend is built with **Flask** (in `flask_server/`).

---

## Project Structure (matches your current repo)

```
RESEARCHPROJECT1/
├─ .venv/                      # Optional: root Python virtual environment (not recommended to commit)
├─ client/                     # React frontend
│  ├─ node_modules/
│  ├─ public/
│  ├─ src/
│  ├─ venv/                    # Can be deleted or ignored in Git
│  ├─ .gitignore
│  ├─ package.json
│  ├─ package-lock.json
│  └─ README.md
├─ flask_server/               # Flask backend
│  ├─ venv/                    # Virtual environment (not recommended to commit)
│  ├─ __init__.py
│  ├─ bert_model.py
│  ├─ bert_search.py
│  ├─ bert_similarity.py
│  ├─ experiment_evaluation.py
│  ├─ export_positive.py
│  ├─ import_csv_to_db.py
│  ├─ model_comparison.py
│  ├─ ollama_parser.py
│  ├─ product_search.py
│  ├─ server_config.py
│  └─ server.py
└─ README.md                   # This file
```

> Note: Both `venv/` and `.venv/` are virtual environments and should generally **not** be committed to Git.

---

## Quick Start

### 1) Start Backend (Flask)

```bash
# Go to backend directory
cd flask_server

# Create and activate virtual environment (skip if already done)
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies (if no requirements.txt, install manually)
# pip install -r requirements.txt
pip install flask pandas numpy scikit-learn sentence-transformers

# Option A: Run with flask run (recommended)
export FLASK_APP=flask_server         # Windows: set FLASK_APP=flask_server
export FLASK_ENV=development          # Optional
flask run -p 8900                     # Default: http://127.0.0.1:8900

# Option B: If you have server.py
# python server.py
```

### 2) Start Frontend (React)

```bash
# Go to frontend directory
cd client

# Install dependencies
npm install

# Start dev server
npm start                              # CRA default: http://localhost:3000
# If using Vite: npm run dev
```

### 3) Configure Frontend API URL

In `client`, set backend API URL via `.env` file:

- **Create React App**:  

  ```env
  REACT_APP_API_BASE=http://127.0.0.1:8900
  ```

- **Vite**:  

  ```env
  VITE_API_BASE=http://127.0.0.1:8900
  ```

In frontend code, load the env variable:

```js
const API_BASE = import.meta?.env?.VITE_API_BASE || process.env.REACT_APP_API_BASE || "http://127.0.0.1:8900";
```

---

## Example API Endpoint

- `POST /search_by_bert`  
  **Body**: `{"query": "fresh perfume for summer"}`  
  **Response**: Top-N recommended perfumes (with similarity/score fields)

> Check actual endpoints in your Flask code (`flask_server/bert_search.py` etc.).

---

## Evaluation (example results)

| Method                | Precision@5 | NDCG@5 |
| --------------------- | ----------- | ------ |
| Keyword Match         | 0.00        | 0.00   |
| Semantic Match        | 0.50        | 0.50   |
| Hybrid Recommendation | 0.68        | 0.68   |

---

## Git Ignore Recommendation

In `.gitignore`:

```
# macOS
.DS_Store

# Node
node_modules/
client/node_modules/

# Python venv
venv/
.venv/
client/venv/
flask_server/venv/

# Python cache
__pycache__/
*.pyc
```

If already committed:

```bash
git rm -r --cached node_modules client/node_modules venv .venv client/venv flask_server/venv
git commit -m "chore: remove ignored folders"
git push
```

---

## Ports

- Backend: `http://127.0.0.1:8900`
- Frontend (CRA): `http://localhost:3000` (Vite: `5173`)

---

## License

MIT License

