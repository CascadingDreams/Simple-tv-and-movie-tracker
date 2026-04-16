#!/bin/bash
set -e

echo "Parsing database connection from DATABASE_URL..."
# DATABASE_URL format: postgresql://user:password@host:port/dbname
DB_HOST=$(echo "$DATABASE_URL" | sed -E 's|.*@([^:/]+)[:/].*|\1|')
DB_PORT=$(echo "$DATABASE_URL" | sed -E 's|.*@[^:]+:([0-9]+)/.*|\1|')
DB_USER=$(echo "$DATABASE_URL" | sed -E 's|.*://([^:]+):.*|\1|')

# Default port if not present in URL
DB_PORT=${DB_PORT:-5432}

echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" 2>/dev/null; do
  >&2 echo "Database is unavailable - sleeping"
  sleep 2
done
echo "Database is ready."

echo "Running migrations..."
flask db upgrade

echo "Starting application with gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app
