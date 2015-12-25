import os


def env(key, default):
    return os.environ.get(key, default)


DEBUG = env('DEBUG', False)

SECRET_KEY = env('OAUTH_SECRET_KEY', 'super secret development key')

SQLALCHEMY_DATABASE_URI = env('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = env('SQLALCHEMY_TRACK_MODIFICATIONS', False)
SQLALCHEMY_ECHO = env('SQLALCHEMY_ECHO', False)
