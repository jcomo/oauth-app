from oanalytics.app import db
from oanalytics.utils import random_id

_SCOPE_DESCRIPTIONS = {
    'read_public_profile': 'Read public profile information',
    'read_analytics': 'Read analytics data',
}


def friendly_scopes(scopes):
    return [_SCOPE_DESCRIPTIONS[scope] for scope in scopes]


def scopes_valid(scopes):
    return scopes and all(scope in _SCOPE_DESCRIPTIONS for scope in scopes)


class OAuthApplication(db.Model):
    __tablename__ = 'oauth_application'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    client_id = db.Column(db.String(40), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    redirect_uri = db.Column(db.String(80), nullable=False)
    icon_url = db.Column(db.String(80))
    website_url = db.Column(db.String(80))
    grants = db.relationship('OAuthGrant',
                             lazy='dynamic',
                             backref=db.backref('application', lazy='joined'))

    def __init__(self, user, name, redirect_uri, icon_url=None, website_url=None):
        self.user = user
        self.name = name
        self.redirect_uri = redirect_uri
        self.icon_url = icon_url
        self.website_url = website_url
        self.client_id = random_id(32)

    @classmethod
    def by_client_id(cls, client_id):
        return cls.query.filter_by(client_id=client_id).first()


class OAuthGrant(db.Model):
    __tablename__ = 'oauth_grant'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('oauth_application.id'), nullable=False)
    redirect_uri = db.Column(db.String(80), nullable=False)
    scopes = db.Column(db.String(400), nullable=False)
    code = db.Column(db.String(80), nullable=False)

    def __init__(self, user, application, scopes):
        self.user = user
        self.application = application
        self.redirect_uri = application.redirect_uri
        self.scopes = '|'.join(scopes)
        self.code = random_id(32)
