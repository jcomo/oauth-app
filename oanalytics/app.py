from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

from oanalytics.analytics import analytics
from oanalytics.oauth import oauth

app.register_blueprint(oauth, url_prefix='/oauth')
app.register_blueprint(analytics, url_prefix='/analytics')
