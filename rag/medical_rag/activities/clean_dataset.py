from temporalio import activity
import pandas as pd

#matlab yeh function bhi Temporal workflow ke andar ek trackable "step" ban jayega
@activity.defn
async def clean_dataset(input_path): # yeh read data activity se data ko as received input path accept karega
    print("Cleaning medical dataset...")

    df = pd.read_pickle(input_path)  # disk se wapis DataFrame ki shakal mein load kiya ja raha hai
    print(f"Before cleaning: {len(df)} records")

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"]) # remove the unuseful name column remove thorugh drop

    df = df.dropna(subset=['transcription']) # subset show that just transcription column have Nan , mssing value so remove it 
    print(f"After cleaning: {len(df)} records")

    output_path = "rag/medical_rag/data/step2_clean.pkl"
    df.to_pickle(output_path)

    print(f"Saved to: {output_path}")
    return output_path