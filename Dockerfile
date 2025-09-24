FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y build-essential

# Copier le fichier requirements
COPY requirements.txt .

# Mettre à jour pip
RUN pip install --upgrade pip

# Installer numpy séparément pour éviter les conflits
RUN pip install --no-cache-dir numpy==1.26.4

# Installer les autres dépendances et gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copier le code de l'application
COPY . .

# Définir les variables d'environnement
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000

# Exposer le port
EXPOSE 8000

# Démarrer l'application avec gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
