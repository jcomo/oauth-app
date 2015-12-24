from flask_testing import TestCase as FlaskTestCase

from app import app, db


class TestCase(FlaskTestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        db.create_all()

    def tearDown(self):
        db.drop_all()
        super(TestCase, self).tearDown()

    def create_app(self):
        app.config['DEBUG'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def get_cookie(self, cookie_name):
        cookies = self.client.cookie_jar
        possible_cookies = iter(c for c in cookies if cookie_name == c.name)
        cookie = next(possible_cookies, None)
        if cookie:
            return cookie.value
