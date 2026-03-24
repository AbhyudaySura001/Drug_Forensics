from fastapi import FastAPI, UploadFile, File
import hashlib
import sqlite3
import pandas as pd
import pickle   # 👈 ADD THIS

from messenger_forensics import extract_messages

app = FastAPI(docs_url="/docs", redoc_url=None)

# 👇 LOAD MODEL ON START
clf = pickle.load(open("drug_classifier.pkl", "rb"))
vec = pickle.load(open("tfidf_vectorizer.pkl", "rb"))

@app.get("/")
def home():
    return {"message": "ML service running perfectly"}

@app.post("/analyse")
async def analyse(file: UploadFile = File(...)):
    contents = await file.read()

    # Save file temporarily
    temp_path = "temp.db"
    with open(temp_path, "wb") as f:
        f.write(contents)

    # Hash
    sha256 = hashlib.sha256(contents).hexdigest()

    # Connect to DB
    conn = sqlite3.connect(temp_path)

    # Extract messages
    df = extract_messages(conn)

    conn.close()

    # 🚀 ADD ML HERE (THIS IS THE IMPORTANT PART)
    X = vec.transform(df["text"].fillna(""))
    df["ml_score"] = clf.predict_proba(X)[:, 1]
    def risk(score):
        if score > 0.85:
            return "HIGH"
        elif score > 0.7:
            return "MEDIUM"
        else:
            return "LOW"

    df["risk_level"] = df["ml_score"].apply(risk)

    return {
        "sha256": sha256,
        "messages": df.to_dict(orient="records")
    }