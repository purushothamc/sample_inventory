from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.secret_key = 'development key'
basedir = os.path.abspath(os.path.dirname(__file__))

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config['MAIL_USE_TLS'] = False
app.config["MAIL_USERNAME"] = 'purush.bb10@gmail.com'
app.config["MAIL_PASSWORD"] = 'cvssrmbpm'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:cvssrmbpm@localhost/production'

db = SQLAlchemy()
db.init_app(app=app)

@app.before_first_request
def create_database():
     db.create_all()

from .routes import mail
mail.init_app(app)

import flask_app.routes
