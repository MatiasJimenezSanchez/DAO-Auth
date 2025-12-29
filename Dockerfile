FROM python:3.12-slim

WORKDIR /app

# Install build deps + postgres client tools (pg_isready/psql, postgesql-client)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN chmod +x /app/scripts/wait-for-db.sh

EXPOSE 8000

CMD ["/app/scripts/wait-for-db.sh"]
