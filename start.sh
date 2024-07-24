#!/bin/sh
 celery -A celery_task.celery_app worker --loglevel=info &
uvicorn main:app --host 127.0.0.1 --port 8000
