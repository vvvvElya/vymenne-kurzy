web: gunicorn exchange_rates.wsgi --bind 0.0.0.0:$PORT
worker: celery -A exchange_rates worker --loglevel=info
beat: celery -A exchange_rates beat --loglevel=info
