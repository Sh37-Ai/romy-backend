import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import firebase_admin
from firebase_admin import credentials, firestore


# --- Localiser le CSV ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # dossier du script
CSV_PATH = os.path.join(BASE_DIR, "rorschach_30000_9reponses_corr.csv")
print("Chemin utilisé :", CSV_PATH)

# --- Charger le dataset ---
df = pd.read_csv(CSV_PATH, encoding="utf-8")
print("Aperçu des données :")
print(df.head())

# --- Séparer les features et le label ---
X = df.drop("Label", axis=1)  # Les 9 réponses
y = df["Label"]

# --- One-Hot Encoding des réponses ---
X_encoded = pd.get_dummies(X)

# --- Séparer train/test ---
X_train, X_test, y_train, y_test = train_test_split(
    X_encoded, y, test_size=0.2, random_state=45
)

# --- Entraîner le Random Forest ---
model = RandomForestClassifier(n_estimators=1000, random_state=45)
model.fit(X_train, y_train)

# --- Évaluation ---
y_pred = model.predict(X_test)
print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nRapport de classification :\n", classification_report(y_test, y_pred))

# --- Exemple de test ---
test_example = pd.DataFrame([['Deux personnages', 'Animaux puissants', 'Deux personnages', 'Figures menaçantes', 'Animaux puissants', 'Deux personnages', 'Figures menaçantes', 'Deux personnes', 'Animaux puissants']
],
                            columns=X.columns)
test_encoded = pd.get_dummies(test_example).reindex(columns=X_encoded.columns, fill_value=0)
prediction = model.predict(test_encoded)
print("\nExemple de prédiction :", prediction[0])





