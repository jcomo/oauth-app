import os


def env(key, default):
    return os.environ.get(key, default)


DEBUG = env('DEBUG', False)

SECRET_KEY = env('SECRET_KEY', 'super secret development key')

OAUTH_BASE_URL = env('OAUTH_BASE_URL', '')
APP_CLIENT_ID = env('APP_CLIENT_ID', '')
