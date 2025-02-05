#!/bin/sh

# Flask server
pip install --upgrade flask==1.1.2
pip install --upgrade flask-sqlalchemy==2.5.1
pip install --upgrade flask-migrate==2.7.0
pip install --upgrade flask-marshmallow==0.14.0
pip install --upgrade marshmallow-sqlalchemy==0.24.2
pip install --upgrade flask-cors==3.0.10
pip install --upgrade marshmallow_enum==1.5.1
pip install --upgrade jinja2==2.11.3
pip install --upgrade markupsafe==1.1.1
pip install --upgrade itsdangerous==1.1.0
pip install --upgrade werkzeug==1.0.1

# Testing
pip install --upgrade flask-testing==0.8.1

# Database
pip install --upgrade psycopg2-binary==2.8.6

# Google Sign-In API
pip install --upgrade google-api-python-client==2.9.0

# JSON Web Token
pip install --upgrade pyjwt==2.1.0

# Analysis
pip install --upgrade pandas==1.4.1
