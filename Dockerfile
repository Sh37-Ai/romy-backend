FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir numpy==1.26.4
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# ⚠️ Utiliser la forme shell pour que $PORT soit substitué
CMD gunicorn app:app --bind 0.0.0.0:$PORT
