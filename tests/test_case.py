from flask import url_for
from flask_testing import TestCase as FlaskTestCase

from oanalytics.app import app, db
from oanalytics.identity.routes import sessions


class TestCase(FlaskTestCase):
    def create_app(self):
        app.config['DEBUG'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def login_as(self, user):
        session_id = sessions.create(user)
        self.client.set_cookie('localhost', 'session_id', session_id)
        return session_id

    def get_cookie(self, cookie_name):
        cookies = self.client.cookie_jar
        possible_cookies = iter(c for c in cookies if cookie_name == c.name)
        cookie = next(possible_cookies, None)
        if cookie:
            return cookie.value

    def setUp(self):
        super(TestCase, self).setUp()
        db.create_all()

    def tearDown(self):
        db.drop_all()
        sessions.clear()
        super(TestCase, self).tearDown()
