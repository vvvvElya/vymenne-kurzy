web: gunicorn exchange_rates.wsgi --bind 0.0.0.0:$PORT --workers=1
worker: celery -A exchange_rates worker --loglevel=info --concurrency=1
beat: celery -A exchange_rates beat --loglevel=info
