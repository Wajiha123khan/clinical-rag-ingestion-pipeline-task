from temporalio import activity
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter # yeh LangChain ki class hai jo lambe text ko smartly chhote chunks mein todhti hai (sirf character count se nahi kaatti, balke koshish karti hai ke sentences/paragraphs beech mein na tootein, jahan tak mumkin ho)

@activity.defn
async def chunk_dataset(input_path):
    print("Chunking medical dataset...")

    df = pd.read_pickle(input_path)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, # har chunk zyada se zyada 500 characters ka hoga
        chunk_overlap=100 # Consecutive chunks ke beech 100 characters ka overlap hoga

        # chunk 2 apne shuru ke 100 characters mein chunk 1 ke aakhri 100
        # characters repeat karega. Isse context continuity maintain rehti hai, 
        # koi sentence beech mein "kat" ke apna matlab nahi khota.
    ) 

    all_chunks = [] # saare chunks (with unka metadata) collect karenge.
    for _, row in df.iterrows(): # yeh tuple deta hai jisme do values hoti hain (index, row_data) , _ yeh value ignore karegi index nhi chahiye
        transcription = row["transcription"]

        if pd.isna(transcription): # isna check safety for mistakenly NAN pr empty value , check dobara hota hai (fresh, is naye row ke liye)
            continue # if data is Nan so it skip and go to nect record 

        chunks = text_splitter.split_text(transcription)
        for chunk in chunks:
            all_chunks.append({
                "description": row["description"],
                "medical_specialty": row["medical_specialty"],
                "sample_name": row["sample_name"],
                "keywords": row["keywords"],
                "chunk": chunk
            })

    print(f"Total chunks created: {len(all_chunks)}")

    chunks_df = pd.DataFrame(all_chunks)
    output_path = "rag/medical_rag/data/step3_chunks.pkl"
    chunks_df.to_pickle(output_path)

    print(f"Saved to: {output_path}")
    return output_path