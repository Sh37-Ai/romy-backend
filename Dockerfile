# Utiliser Python 3.8
FROM python:3.8-slim

WORKDIR /app

# Installer les dépendances système nécessaires pour pandas / scikit-learn
RUN apt-get update && apt-get install -y build-essential

# Copier les dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code
COPY . .

# Variables d'environnement pour Flask
ENV FLASK_APP=.
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000

# Exposer le port
EXPOSE 8000

# Commande pour lancer Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000", "--reload"]


