from flask import Flask, request, jsonify
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# --- Initialiser Firebase une seule fois ---
JSON_PATH = os.environ.get("SERVICE_ACCOUNT_PATH", "/run/secrets/serviceAccountKey.json")

COLLECTION_NAME = "choixxx"

if not firebase_admin._apps:
    cred = credentials.Certificate(JSON_PATH)
    firebase_admin.initialize_app(cred)
    print("Connexion à Firebase réussie ✅")
db = firestore.client()

# --- Charger le dataset et entraîner le modèle une seule fois ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "rorschach_30000_10reponses_corr1.csv")
df = pd.read_csv(CSV_PATH, encoding="utf-8")

X = df.drop("Label", axis=1)
y = df["Label"]
X_encoded = pd.get_dummies(X)

X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=45)
model = RandomForestClassifier(n_estimators=1000, random_state=45)
model.fit(X_train, y_train)

# --- Fonction pour récupérer les réponses d’un utilisateur ---
def get_user_choices(user_uid):
    try:
        docs = db.collection(COLLECTION_NAME).where("UserId", "==", user_uid).get()
        if not docs:
            return None
        for doc in docs:
            data = doc.to_dict()
            return data.get("valeur", [])
    except Exception as e:
        print("Erreur Firebase :", e)
        return None

# --- Route pour prédire depuis le front ---
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    user_uid = data.get("user_uid")
    if not user_uid:
        return jsonify({"error": "user_uid manquant"}), 400

    user_choices = get_user_choices(user_uid)
    if not user_choices:
        return jsonify({"error": "Aucune réponse trouvée pour cet utilisateur"}), 404

    # --- Créer DataFrame et encoder ---
    test_example = pd.DataFrame([user_choices], columns=X.columns)
    test_encoded = pd.get_dummies(test_example).reindex(columns=X_encoded.columns, fill_value=0)

    # --- Prédiction ---
    prediction = model.predict(test_encoded)
    return jsonify({"prediction": prediction[0]})

if __name__ == "__main__":
    app.run(debug=True)
