from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.identity.session import SessionStore

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

sessions = SessionStore()

from app.identity.routes import identity
from app.analytics.routes import analytics
from app.oauth.routes import oauth

app.register_blueprint(identity, url_prefix='/identity')
app.register_blueprint(analytics, url_prefix='/analytics')
app.register_blueprint(oauth, url_prefix='/oauth')
