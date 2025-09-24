from flask import Flask, request, jsonify
import os
import pandas as pd
import joblib
import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- Initialiser Firebase ---
JSON_PATH = os.environ.get(
    "SERVICE_ACCOUNT_PATH",
    os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")  # fallback local
)
COLLECTION_NAME = "choixxx"

if not firebase_admin._apps:
    cred = credentials.Certificate(JSON_PATH)
    firebase_admin.initialize_app(cred)
    print("Connexion à Firebase réussie ✅")
db = firestore.client()

# --- Charger le modèle pré-entraîné compressé ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model1.pkl")
model = joblib.load(MODEL_PATH)  # modèle compressé avec joblib.dump(model, "model.pkl", compress=3)

# --- Charger les colonnes encodées pour préparer les nouvelles données ---
CSV_PATH = os.path.join(BASE_DIR, "rorschach_30000_10reponses_corr1.csv")
df = pd.read_csv(CSV_PATH, encoding="utf-8")
X = df.drop("Label", axis=1)
X_encoded = pd.get_dummies(X)

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
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
