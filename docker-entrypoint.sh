#!/bin/bash
set -e

echo "Initializing database..."
python -m scripts.init_db

echo "Initializing admin..."
python -m scripts.init_admin

echo "Starting Uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
