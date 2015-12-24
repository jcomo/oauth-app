import bcrypt

from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    oauth_applications = db.relationship('OAuthApplication',
                                         lazy='dynamic',
                                         backref=db.backref('user', lazy='joined'))
    oauth_grants = db.relationship('OAuthGrant',
                                   lazy='dynamic',
                                   backref=db.backref('user', lazy='joined'))

    def __init__(self, name, username=None, password=None):
        self.name = name
        self.username = username
        if password:
            self.password_hash = self._hash_password(password)

    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def _password_matches(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), self.password_hash.encode('utf-8')) == self.password_hash

    @classmethod
    def by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def register(cls, name, username, password):
        user = cls(name, username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return user

    @classmethod
    def login(cls, username, password):
        user = cls.by_username(username)
        if user and user._password_matches(password):
            return user
