# Agentic Clinical RAG — Data Ingestion Pipeline

A Temporal-orchestrated data ingestion pipeline that processes clinical transcription data, generates embeddings, and stores them in a vector database for downstream Retrieval-Augmented Generation (RAG) use cases.

This is **Phase 1–5** of a larger project. The current pipeline implements a **Classic/Naive RAG ingestion flow**. A future phase will add a **LangGraph-based agentic layer** (multi-agent orchestration with a validator agent) on top of this foundation.

---

## Overview

The pipeline takes raw clinical transcription records, cleans them, splits them into semantically meaningful chunks, generates vector embeddings for each chunk, and stores everything in a PostgreSQL database with `pgvector` for similarity search.

Every step is implemented as an independent **Temporal activity**, orchestrated by a single **Temporal workflow**, and the entire stack runs in Docker.

---

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   read_dataset   │───▶│  clean_dataset   │───▶│  chunk_dataset   │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                                                          │
                                                          ▼
                              ┌──────────────────┐    ┌──────────────────┐
                              │  store_pgvector  │◀───│generate_embeddings│
                              └──────────────────┘    └──────────────────┘
```

Each activity:
1. Reads its input from a `.pkl` file path (not raw data)
2. Performs its transformation
3. Saves its output to a new `.pkl` file
4. Returns only the **file path** to the next activity

This **data-by-reference pattern** was adopted specifically to work around Temporal's ~4MB gRPC payload limit, which makes passing large DataFrames directly between activities impossible.

---

## Tech Stack

| Component | Technology |
|---|---|
| Workflow orchestration | Temporal.io (Python SDK) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (384-dim) |
| Vector storage | PostgreSQL + `pgvector` extension |
| Text splitting | LangChain `RecursiveCharacterTextSplitter` |
| Containerization | Docker & Docker Compose |
| Dataset | [Kaggle mtsamples](https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions) (medical transcriptions) |

---

## Pipeline Steps

| Step | Activity | Description |
|---|---|---|
| 1 | `read_dataset` | Reads `mtsamples.csv` (4,999 records) |
| 2 | `clean_dataset` | Drops null transcriptions and unused columns → 4,966 records |
| 3 | `chunk_dataset` | Splits transcriptions into 500-character chunks (100-char overlap) → 39,156 chunks |
| 4 | `generate_embeddings` | Batch-encodes all chunks into 384-dim vectors |
| 5 | `store_pgvector` | Inserts all chunks + embeddings into the `medical_chunks` table |

---

## Project Structure

```
medical_rag_docker/
├── rag/medical_rag/
│   ├── activities/
│   │   ├── read_dataset.py
│   │   ├── clean_dataset.py
│   │   ├── chunk_dataset.py
│   │   ├── generate_embeddings.py
│   │   └── store_pgvector.py
│   ├── data/
│   │   └── mtsamples.csv
│   ├── workflow.py       # Temporal workflow definition
│   ├── worker.py          # Temporal worker (executes activities)
│   └── starter.py         # Triggers a workflow execution
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Running the Project

### 1. Start all services

```bash
docker compose up -d
```

This starts 6 containers:
- `temporal-postgresql` — Temporal's internal metadata store
- `temporal` — Temporal server
- `temporal-ui` — Web UI at `http://localhost:8080`
- `temporal-admin-tools` — CLI tools for Temporal
- `pgvector-db` — Vector database at port `5433`
- `medical-rag-worker` — Executes the pipeline activities

### 2. Trigger the pipeline

```bash
python rag/medical_rag/starter.py
```

This starts a new workflow execution. Progress can be monitored live at `http://localhost:8080`.

> ⚠️ Note: Re-running `starter.py` without clearing the `medical_chunks` table will insert duplicate rows, since `store_pgvector` does not currently check for existing data.

---

## Results

A full pipeline run produces:

- **4,966** cleaned clinical records
- **39,156** text chunks
- **39,156** corresponding 384-dimensional embeddings
- All stored in the `medical_chunks` table:

```sql
CREATE TABLE medical_chunks (
    id SERIAL PRIMARY KEY,
    description TEXT,
    medical_specialty TEXT,
    sample_name TEXT,
    keywords TEXT,
    chunk TEXT,
    embedding VECTOR(384)
);
```

---

## Key Engineering Decisions

- Data-by-reference pattern: Activities pass file paths, not DataFrames, to stay under Temporal's gRPC payload limit.
- Batch encoding: Embeddings are generated in batches (`batch_size=64`) rather than one at a time, which was critical for avoiding activity timeouts on CPU.
- Long timeout on embedding step: `generate_embeddings` is given a 90-minute `start_to_close_timeout` since it is the most compute-heavy step (~20–25 minutes for the full dataset on CPU).
- Chunk overlap: A 100-character overlap between chunks preserves context continuity across chunk boundaries.

---
