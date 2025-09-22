web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --worker-class gevent --timeout 120 --keepalive 2 --max-requests 1000 --access-logfile - --error-logfile - wsgi:app
worker: celery -A app_enhanced.celery worker --loglevel=info --concurrency=2
beat: celery -A app_enhanced.celery beat --loglevel=info
