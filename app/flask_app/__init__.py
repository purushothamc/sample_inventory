from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.secret_key = 'development key'
basedir = os.path.abspath(os.path.dirname(__file__))

# Send Mail server configuration
app.config["MAIL_SERVER"] = "smtp.rim.net"
app.config["MAIL_PORT"] = 25
app.config["MAIL_USE_SSL"] = False
app.config['MAIL_USE_TLS'] = False
app.config["MAIL_USERNAME"] = None
app.config["MAIL_PASSWORD"] = None
app.config['MAIL_DEFAULT_SENDER'] = "hyd_inventory@blackberry.com"

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:blackberry@localhost/production'

db = SQLAlchemy()
db.init_app(app=app)

@app.before_first_request
def create_database():
     db.create_all()

from .routes import mail
mail.init_app(app)

import flask_app.routes
