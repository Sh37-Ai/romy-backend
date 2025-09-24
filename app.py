from flask import Flask, request, jsonify
import os
import pandas as pd
import joblib
import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- Clé Firebase directement dans le code ---
firebase_key = {
    "type": "service_account",
    "project_id": "romy-1c993",
    "private_key_id": "3d9a7fe7d5afc6d01dd369e4a29aa1e9598db9fa",
    "private_key": """-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCxmehItCwlCQF2\nPKdFs+VxNruzGHrOuI/uv577vYCjFvHDrfAGh6JmpdmYRvd+ZFltCK5rWUsJ1X5A\nOoV4LzA8YFPKxvySLWB5H3h+SxaHsASsE4xJuWlq23isDSMvgNymSbIl2AVUdsxW\nuE3qF5h6nYscQxB4SW2dLO9XkMfbydbX1KPZ1LepGIvQzaKVDHWJ0gnD4H6iEIdP\nQuzIM5uN0B6Os6ZSmKMUvAb8rrEBcAvzFNj9Lvv84Po0XJaorr26j9DZuuc6/UG2\n7j0CmDsqnv9rhw9AwySIaDpUEXfVi7sAdVHPyxmN610b7fxqEBzdyQSTB/hW8YvO\nwO1FbVAdAgMBAAECggEAEUP1lXp9NNKAeQv3dQAX+klzC5EB1gPnljMRvnETRtzt\nqZ4eEKccmMm0ctMqBKMLyzJGBpCaihJeYNnE7O9QIKZ6ruK+XhWZjzI0hrk/r6GN\n1WQHG4myCl3bXYU0xPhMOxbnVzooy9J1a1QlMEXqoGJIH6S+E/uLc6ARL9xBhF0b\n1M1u0oEUI/2tPtKuRz15oTAl90S2hOLr12gewKOu6fPC7mFHsiIhH6mof8jH1Nzr\nBv6DKATHRlRshWAvoU/s07eVlfORMTWrxYUl9JcMa57SeFJkzTqgqxDLxexdxVgo\nNq4QygJg5oEOEVboPOVL27S4lXVImSaP5H3kSBqpDwKBgQD2IUfjQ/ExqCTgcbPd\nKi9nWZ+pEzq4kW5rwq1Euwod36Q++lLs6Vja0yEAqc/fM3fKtELM6NzebvcY6p+3\nKlhQXVhvF66Q4n6Knulx58OsHvevL/qnwT9QM31qvrWvyGl/r3SIRAGaR43VdZoV\npBvSwgKLdu246jZgkbT460nwpwKBgQC4uR/KK9QHIRxWJcWifWq9K4m7VBAzoMBm\n0mMke0tNFuBHBtMya3WdT6TqhwcK9NCUnHQ+x6a7SY0N8aOnCgt4eaQqoNGshdn5\nSM08xifEPQhyiOOV4B6jPHLL8DBWhJ8gGa7EAu40xvrbFUnkranYDEFqVgdfsVcp\nzZ0A8vLtmwKBgH8lPByj2XIceUhUlGS4yRorizXtUBVOU2tpetaZhKVgBVnfOH1Y\nIeWQ0WilUFPuI4DcU/HEjWx+iDkf4vfc8Rg60Fc7NZt01YfIhbGo10UQDkU6lNKa\nGpnUr4I4GGVBM3aZbaqC7w0Cz7socDujthfOzz+6ZR10KDkErCc2bNDbAoGAQevu\n6FtTw2eRkTzRlvdjDDdpY6zQS1xmzUrvjqlhahVr3G0XGbs3sfgmRnwBi2tqtF5R\nLcZaPiQ1bnB5krcG+OuQJpZVvVfXPhs5AyNENcgCJ72qWmYtCNwdq6H/3iBeGTqR\nH+pb0AHirCSgxjcjkbJt9eDVqNTE4mo6SYhqIVkCgYAPgNgYz3S/blmhZu6QH0rj\nAdekikgWVwPuzOb/9752wiWP0CZxo6/e+BmzAtgOF8I0EvPbW+vDNO6VMViDdk28\nSFqXfPT9kYcLClt9OKK9/OLaaOkstFKPsndPqZ00Efw5MBgdLv8SQk3ASSb8OeJa\n4qlnVN6i+NgCFKS8xEt6gQ==\n-----END PRIVATE KEY-----""",
    "client_email": "firebase-adminsdk-fbsvc@romy-1c993.iam.gserviceaccount.com",
    "client_id": "101600039449809746777",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc@romy-1c993.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# --- Initialisation Firebase ---
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred)
db = firestore.client()

COLLECTION_NAME = "choixxx"

# --- Charger le modèle pré-entraîné ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model1.pkl")
model = joblib.load(MODEL_PATH)

# --- Charger les colonnes encodées ---
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

# --- Route prédiction ---
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    user_uid = data.get("user_uid")
    if not user_uid:
        return jsonify({"error": "user_uid manquant"}), 400

    user_choices = get_user_choices(user_uid)
    if not user_choices:
        return jsonify({"error": "Aucune réponse trouvée pour cet utilisateur"}), 404

    test_example = pd.DataFrame([user_choices], columns=X.columns)
    test_encoded = pd.get_dummies(test_example).reindex(columns=X_encoded.columns, fill_value=0)
    prediction = model.predict(test_encoded)
    return jsonify({"prediction": prediction[0]})

# --- Health check ---
@app.route("/healthz", methods=["GET"])
def healthz():
    return "OK", 200

# --- Démarrage du serveur ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Railway fournit le port automatiquement
    app.run(debug=True, host="0.0.0.0", port=port)
