# Utiliser Python 3.10
FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y build-essential

# Copier requirements.txt
COPY requirements.txt .

# Mettre à jour pip et installer numpy en premier pour éviter les incompatibilités
RUN pip install --upgrade pip
RUN pip install --no-cache-dir numpy==1.26.4
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code
COPY . .

# Variables d'environnement pour Flask
ENV FLASK_APP=.
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000

# Exposer le port
EXPOSE 8000

# Lancer avec gunicorn
CMD ["gunicorn", "__init__:app", "--bind", "0.0.0.0:8000"]
