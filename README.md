# Vector Pipeline

Embedding-based document search using Sentence Transformers + Qdrant.

- Ingestion pipeline: fetch → extract → embed → upsert to Qdrant
- FastAPI REST API: semantic search over stored embeddings

## Project Structure

<pre>
vector_pipeline/
├── main.py                  (ingestion entrypoint)
├── main_api.py              (FastAPI API entrypoint)
│
├── app/
│   ├── api/
│   │   └── routes.py
│   └── models/
│       └── query_models.py
│
├── embeddings/
│   └── embedding_generator.py
├── vectorstore/
│   └── qdrant_client.py
├── fetchers/
├── loaders/
├── extractors/
├── text_utils/
└── .env
</pre>

## Prerequisites

- Python 3.9+
- pip
- Docker (to run Qdrant locally)

## Environment Variables

| Variable Name         | Description                                | Default Value |
|------------------------|--------------------------------------------|----------------|
| `QDRANT_HOST`          | Host address of the Qdrant instance        | `localhost`    |
| `QDRANT_PORT`          | Port number Qdrant listens on              | `6333`         |
| `QDRANT_COLLECTION`    | Name of the Qdrant collection used         | `documents`    |
| `QDRANT_DISTANCE`      | Vector distance metric (`Cosine`, `Dot`, `Euclid`) | `Cosine`       |
| `EMBEDDING_MODEL`      | Name of the SentenceTransformer model      | `sentence-transformers/all-MiniLM-L6-v2` |
| `EMBEDDING_DEVICE`     | Device for model inference (`cpu` or `cuda`) | `cpu`        |
| `LOG_LEVEL`            | Logging level for the application          | `INFO`         |