# Back-end (Flask + uWSGI) image.
# Python 3.9 is required: the pinned Flask 1.1.2 stack does not run on 3.10+.
FROM python:3.9-slim

# build-essential is only needed to compile uWSGI from its sdist; it is removed
# afterwards to keep the image small. psycopg2-binary and pandas ship as wheels.
COPY requirements.txt /app/requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*

# Application code. config.py resolves the secret directory as ../../secret
# relative to www/config, i.e. /app/secret, which is mounted at runtime.
COPY www /app/www

WORKDIR /app/www

# Select the production configuration profile (see config/config.py).
ENV APP_CONFIG=production
# FLASK_APP lets "flask db upgrade" work via `docker compose exec api ...`.
ENV FLASK_APP=application.py

EXPOSE 8080

CMD ["uwsgi", "--ini", "uwsgi_docker.ini"]
