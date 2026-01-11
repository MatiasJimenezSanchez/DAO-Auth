FROM python:3.12-slim

WORKDIR /app

# deps para compilar + cliente de postgres (pg_isready)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev postgresql-client \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/app
COPY . /app

RUN chmod +x /app/scripts/wait-for-db.sh

EXPOSE 8000

CMD ["/app/scripts/wait-for-db.sh"]
