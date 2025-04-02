web: gunicorn exchange_rates.wsgi
worker: celery -A exchange_rates worker --loglevel=info
beat: celery -A exchange_rates beat --loglevel=info
