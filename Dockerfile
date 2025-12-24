FROM python:3.12-slim

WORKDIR /app

# Install build deps (kept minimal since we use psycopg2-binary)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Ensure the wait script is executable and available
RUN chmod +x /app/scripts/wait-for-db.sh

EXPOSE 8000

# Default command: wait for DB, run migrations, then start the app
CMD ["/app/scripts/wait-for-db.sh"]
