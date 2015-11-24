from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from oanalytics.identity.session import SessionStore

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

sessions = SessionStore()

from oanalytics.identity.routes import identity
from oanalytics.analytics.routes import analytics
from oanalytics.oauth.routes import oauth

app.register_blueprint(identity, url_prefix='/identity')
app.register_blueprint(analytics, url_prefix='/analytics')
app.register_blueprint(oauth, url_prefix='/oauth')
