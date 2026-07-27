from temporalio import activity
import pandas as pd
import psycopg2
import os
from psycopg2.extras import execute_values

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5433")


@activity.defn
async def store_pgvector(input_path):
    print("Storing in pgvector...")

    df = pd.read_pickle(input_path)

    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname="clinical_db",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()

    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS medical_chunks (
            id SERIAL PRIMARY KEY,
            description TEXT,
            medical_specialty TEXT,
            sample_name TEXT,
            keywords TEXT,
            chunk TEXT,
            embedding VECTOR(384)
        );
    """)
    conn.commit()

    rows = [
        (
            row["description"],
            row["medical_specialty"],
            row["sample_name"],
            row["keywords"],
            row["chunk"],
            row["embedding"]
        )
        for _, row in df.iterrows()
    ]

    execute_values(
        cur,
        """
        INSERT INTO medical_chunks
        (description, medical_specialty, sample_name, keywords, chunk, embedding)
        VALUES %s
        """,
        rows
    )
    conn.commit()

    print(f"Inserted {len(rows)} rows into pgvector.")

    cur.close()
    conn.close()

    return f"Stored {len(rows)} chunks in pgvector"