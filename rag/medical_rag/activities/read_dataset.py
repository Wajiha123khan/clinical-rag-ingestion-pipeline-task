import pandas as pd
from temporalio import activity

@activity.defn
async def read_dataset():
    print("Reading dataset...")

    df = pd.read_csv("rag/medical_rag/data/mtsamples.csv")
    print(f"Total records: {len(df)}")

    # Temporal ka kaam hai activities ko chain mein chalana — 
    # ek activity ka output agli activity ka input banta hai.
    # yeh network protocal gRPC protocol ke zariye jaata hain and iski bhi hard limit hoti hain ek message main ziyada tar 

    # 4MB data bhej sakte ho 

    output_path = "rag/medical_rag/data/step1_raw.pkl" # data-by-reference
    df.to_pickle(output_path)

    print(f"Saved to: {output_path}")
    return output_path # sirf yeh string:To Temporal ko sirf yeh chhoti si path string bhejni padti hai — jo sirf kuch bytes ki hai, 4MB se bohot kam. Isliye koi limit cross nahi hoti, koi error nahi aata.