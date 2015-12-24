from datetime import timedelta

from werkzeug.contrib.cache import SimpleCache

from app.utils import random_id

SUGGESTED_KEY = 'session_id'


class ExistingSession(Exception):
    pass


class SessionStore(object):
    def __init__(self):
        self.cache = SimpleCache()
        self.expiration = timedelta(weeks=1).total_seconds()

    def create(self, user):
        session_id = random_id(24)
        existing_session = self.cache.get(session_id)
        if existing_session:
            raise ExistingSession

        self.cache.set(session_id, user.id, timeout=self.expiration)
        return session_id

    def retrieve(self, session_id):
        # TODO: this should optionally refresh the session
        return self.cache.get(session_id)

    def remove(self, session_id):
        self.cache.delete(session_id)

    def clear(self):
        self.cache.clear()
