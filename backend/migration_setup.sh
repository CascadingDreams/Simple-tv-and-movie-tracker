#!/bin/bash

echo "Waiting for database..."
until PGPASSWORD=streamtracker123 psql -h db -U streamtracker -d streamtracker -c '\q' 2>/dev/null; do
  >&2 echo "Database is unavailable"
  sleep 1
done

if [ ! -d "migrations/versions" ]; then
    flask db init
fi

flask db migrate -m "Initial migration"
flask db upgrade
python3 app.py
