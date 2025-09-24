from flask import Flask, request, jsonify
import os
import pandas as pd
import joblib
import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS
import tempfile
import json

app = Flask(__name__)
CORS(app)

# --- Initialiser Firebase depuis la variable d'environnement ---
COLLECTION_NAME = "choixxx"
sa_json = os.environ.get("SERVICE_ACCOUNT_JSON")
if not sa_json:
    raise Exception("SERVICE_ACCOUNT_JSON non défini !")

# Créer un fichier temporaire pour Firebase
with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
    f.write(sa_json)
    f.flush()
    cred = credentials.Certificate(f.name)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Charger le modèle et les colonnes encodées ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model1.pkl")
model = joblib.load(MODEL_PATH)

CSV_PATH = os.path.join(BASE_DIR, "rorschach_30000_10reponses_corr1.csv")
df = pd.read_csv(CSV_PATH, encoding="utf-8")
X = df.drop("Label", axis=1)
X_encoded = pd.get_dummies(X)

# --- Route predict ---
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    user_uid = data.get("user_uid")
    if not user_uid:
        return jsonify({"error": "user_uid manquant"}), 400

    docs = db.collection(COLLECTION_NAME).where("UserId", "==", user_uid).get()
    if not docs:
        return jsonify({"error": "Aucune réponse trouvée pour cet utilisateur"}), 404
    for doc in docs:
        user_choices = doc.to_dict().get("valeur", [])

    test_example = pd.DataFrame([user_choices], columns=X.columns)
    test_encoded = pd.get_dummies(test_example).reindex(columns=X_encoded.columns, fill_value=0)
    prediction = model.predict(test_encoded)
    return jsonify({"prediction": prediction[0]})

# --- Route health check ---
@app.route("/healthz", methods=["GET"])
def healthz():
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
