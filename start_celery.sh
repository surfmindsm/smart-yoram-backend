#!/bin/bash

# Start Celery worker
echo "Starting Celery worker..."
celery -A app.core.celery_app worker --loglevel=info --concurrency=4 &

# Start Celery beat (scheduler)
echo "Starting Celery beat..."
celery -A app.core.celery_app beat --loglevel=info &

# Start Flower (Celery monitoring)
echo "Starting Flower..."
celery -A app.core.celery_app flower --port=5555 &

echo "All Celery services started!"
echo "Flower monitoring available at http://localhost:5555"

# Keep the script running
wait