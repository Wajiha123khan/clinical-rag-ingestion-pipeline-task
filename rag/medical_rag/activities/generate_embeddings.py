from temporalio import activity
from sentence_transformers import SentenceTransformer
import pandas as pd

model = SentenceTransformer("all-MiniLM-L6-v2")

@activity.defn
async def generate_embeddings(input_path):
    print("Generating embeddings...")

    df = pd.read_pickle(input_path)

    texts = df["chunk"].tolist() # df["chunk"] srf chunk wali column lega
    embeddings = model.encode(texts, batch_size=64, show_progress_bar=True).tolist() # Bacth size chunks ko groups mein model ke paas bhejta hai. show_prgrees bar jo teminal main dikht ahai
    df["embedding"] = embeddings # ek translator hai:yeh data frame main emdiing colum add kiya hai

    print(f"Generated embeddings: {len(df)}")

    output_path = "rag/medical_rag/data/step4_embedded.pkl"
    df.to_pickle(output_path)

    print(f"Saved to: {output_path}")
    return output_path