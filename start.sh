#!/bin/bash
echo "Starting gunicorn with 4 workers on port 8080"

exec gunicorn app:app \
    --bind 0.0.0.0:8080 \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker