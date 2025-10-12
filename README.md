🧠 Vector Pipeline

Unified project for embedding-based document search using
Sentence Transformers
 and Qdrant
.

This repo includes:

🧩 Ingestion pipeline (fetch → extract → embed → upsert to Qdrant)

🌐 FastAPI REST API (semantic search over stored embeddings)

📁 Project Structure
<pre> vector_pipeline/ ├── main.py # Ingestion entrypoint ├── main_api.py # FastAPI API entrypoint │ ├── app/ # REST layer │ ├── api/ │ │ └── routes.py │ └── models/ │ └── query_models.py │ ├── embeddings/ │ └── embedding_generator.py # Thread-safe SentenceTransformer wrapper ├── vectorstore/ │ └── qdrant_client.py # Qdrant setup & client helpers ├── fetchers/ ├── loaders/ ├── extractors/ ├── text_utils/ └── .env </pre>
⚙️ Prerequisites

Python 3.9+

pip

Docker (for running Qdrant locally)

📦 Install Dependencies
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\activate


Then install:

pip install fastapi uvicorn qdrant-client sentence-transformers python-dotenv


Or use:

pip install -r requirements.txt

🧱 Run Qdrant

Start Qdrant with Docker:

docker run -p 6333:6333 qdrant/qdrant


Open http://localhost:6333/dashboard

to confirm it’s running.

🔑 Environment Configuration

Create a .env file in your project root:

QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=documents

🧩 Ingest Data

Run your ingestion pipeline (creates collection if missing and upserts vectors):

python main.py


Flow:

Fetchers → get files

Extractors → parse text

Embeddings → generate vectors

Vectorstore → upsert to Qdrant

🌐 Run the API

Start FastAPI:

uvicorn main_api:app --reload


Then open http://localhost:8000/docs

Example request:

POST /api/search
{
  "query": "What are the benefits of olive oil?",
  "top_k": 3
}

🧠 Notes & Conventions

Use the same embedding model for ingestion and queries.

The collection is only created during ingestion, not during search.

Default dimension for all-MiniLM-L6-v2 is 384 — make sure your Qdrant collection matches.

🧰 Useful Commands
Action	Command
Run Qdrant	docker run -p 6333:6333 qdrant/qdrant
Start API	uvicorn main_api:app --reload
Ingest Data	python main.py
Open Docs	http://localhost:8000/docs

Stop API	Ctrl + C
🔧 Environment Variables
Name	Description	Default
QDRANT_HOST	Qdrant host	localhost
QDRANT_PORT	Qdrant port	6333
QDRANT_COLLECTION	Collection name	documents
📜 License

MIT — free for personal and commercial use.