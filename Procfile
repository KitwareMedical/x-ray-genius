release: ./manage.py migrate && ./manage.py loaddata sampledata
web: gunicorn --bind 0.0.0.0:$PORT xray_genius.wsgi
worker: REMAP_SIGTERM=SIGQUIT celery --app xray_genius.celery worker --loglevel INFO --without-heartbeat
