release: ./manage.py migrate && ./manage.py loaddata sampledata
web: daphne -b 0.0.0.0 -p $PORT xray_genius.asgi:application
worker: REMAP_SIGTERM=SIGQUIT celery --app xray_genius.celery worker --loglevel INFO --without-heartbeat
