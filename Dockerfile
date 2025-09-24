FROM python:3.10-slim

WORKDIR /app

# Installer dépendances système utiles (compilation, crypto, etc.)
RUN apt-get update && apt-get install -y build-essential

# Copier requirements
COPY requirements.txt .

# Mettre à jour pip
RUN pip install --upgrade pip

# Installer numpy en premier pour éviter conflits binaires
RUN pip install --no-cache-dir numpy==1.26.4

# Installer les autres dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Render injecte la variable d'environnement PORT (ex: 10000)
# On s'assure que Gunicorn écoute dessus
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT"]
