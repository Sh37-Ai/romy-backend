FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir numpy==1.26.4

# Installer dépendances + gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# Démarrer l'app avec le port Render
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:$PORT"]
