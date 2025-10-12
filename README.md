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

## Qdrant Setup

Qdrant is an open-source vector database used to store and search embeddings.

### 🧱 1. Run Qdrant with Docker

Use the following command to start Qdrant locally and **keep data persisted** on disk:

```bash
docker run -d \
  -p 6333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  --name qdrant \
  qdrant/qdrant

### 🧱 2. Qdrant Docker Explanation

| Option | Description |
|--------|--------------|
| `-d` | Run the container in detached (background) mode |
| `-p 6333:6333` | Map Qdrant’s default port (6333) to your localhost |
| `-v $(pwd)/qdrant_storage:/qdrant/storage` | Mount local folder `qdrant_storage/` for persistent data storage |
| `--name qdrant` | Assign a name (`qdrant`) to the container for easier management |

### 🧾 3. Verify Qdrant is Running

Check the container status:
```bash
docker ps

You should see a container named qdrant in the list. Then open your browser at:
👉 http://localhost:6333/dashboard

to confirm Qdrant is up and running.

### 💾 4. Persistent storage

All data (collections, embeddings, payloads) are stored in ```qdrant_storage/```

This directory is created automatically in your project root and will survive container restarts.

To completely remove Qdrant and its data:

```bash
docker stop qdrant && docker rm qdrant
rm -rf qdrant_storage
```

### 🔄 5. Restarting Qdrant Later

Once Qdrant is installed, you can easily start or stop it:

```bash
docker start qdrant     # start existing container
docker stop qdrant      # stop it
```