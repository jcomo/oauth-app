import string
import random

from oanalytics.app import db


class OAuthApplication(db.Model):
    __tablename__ = 'oauth_application'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    client_id = db.Column(db.String(40), unique=True, nullable=False)
    redirect_uri = db.Column(db.String(80), nullable=False)
    icon_url = db.Column(db.String(80))
    website_url = db.Column(db.String(80))

    def __init__(self, name, redirect_uri, icon_url=None, website_url=None):
        self.name = name
        self.redirect_uri = redirect_uri
        self.icon_url = icon_url
        self.website_url = website_url
        self.client_id = self._generate_client_id()

    def _generate_client_id(self):
        return ''.join(random.choice(string.ascii_letters + string.digits)
                       for _ in xrange(32))
