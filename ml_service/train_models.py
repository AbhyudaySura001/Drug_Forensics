import pandas as pd
import random
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer

# 🔥 Suspicious phrases
suspicious_templates = [
    "bring the cash",
    "delivery completed",
    "same place tonight",
    "package is ready",
    "drop location confirmed",
    "shipment arrived",
    "keep it discreet",
    "no phones allowed",
    "come alone",
    "deal is set",
    "goods received",
    "pickup scheduled",
    "transfer done",
    "bring the stuff",
    "delivery guy reached",
]

# 😊 Normal conversation
normal_templates = [
    "meeting at 5",
    "submit the assignment",
    "let's have lunch",
    "project discussion tomorrow",
    "call me later",
    "birthday party tonight",
    "movie plan confirmed",
    "exam tomorrow",
    "family dinner",
    "how are you doing",
    "good morning",
    "see you soon",
    "thanks for helping",
    "let's catch up",
    "are you free today",
]

# 🎲 Generate synthetic data
def generate_data(n=500):
    texts = []
    labels = []

    for _ in range(n):
        if random.random() > 0.5:
            text = random.choice(suspicious_templates)
            labels.append(1)
        else:
            text = random.choice(normal_templates)
            labels.append(0)

        # Add noise (makes model stronger)
        text = text + random.choice(["", " bro", " asap", " pls", " now", " ok"])
        texts.append(text)

    return pd.DataFrame({"text": texts, "label": labels})

# 📊 Generate dataset
df = generate_data(1000)

# 🧠 Vectorizer (improved)
vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=500)
X = vectorizer.fit_transform(df["text"])
y = df["label"]

# 🌲 Model (stronger)
clf = RandomForestClassifier(n_estimators=200, random_state=42)
clf.fit(X, y)

# 💾 Save
pickle.dump(clf, open("drug_classifier.pkl", "wb"))
pickle.dump(vectorizer, open("tfidf_vectorizer.pkl", "wb"))

print("✅ Model trained with 1000 samples")