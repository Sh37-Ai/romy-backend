FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .

# Mettre à jour pip
RUN pip install --upgrade pip

# Installer numpy avant les autres packages pour éviter le conflit binaire
RUN pip install --no-cache-dir numpy==1.26.4

# Installer les autres dépendances
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=.
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8000

EXPOSE 8000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:${PORT}"]
