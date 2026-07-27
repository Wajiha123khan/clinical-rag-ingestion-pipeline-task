# slim ligghtweight os hain jo ke 150MB use karega just needed tools
FROM python:3.11-slim

# container main app folder create krke then usmein jo requiremtn.txt hain so inject karega
WORKDIR /app
COPY requirements.txt .
#Container ek one-time build process hai.Ek baar pip install ho gaya, image ban gayi — ab dobara kabhi pip install 
#nahi chalega isi image mein (agar packages change karne hain, to poori nayi image banti hai, scratch se)

RUN pip install --no-cache-dir -r requirements.txt

# ismain yeh important chhezein hain bht Requirements pehle copy karne se, 
#code change par rebuild toh phir bhi lagta hai — 
#bas pip install wala bhaari step cache se skip ho jata hai, isliye rebuild seconds mein hota hai, minutes mein nahi.

COPY rag/ ./rag/

CMD [ "python", "rag/medical_rag/worker.py" ]
