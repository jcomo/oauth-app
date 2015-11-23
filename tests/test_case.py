from flask_testing import TestCase as FlaskTestCase

from oanalytics.app import app, db


class TestCase(FlaskTestCase):
    def create_app(self):
        app.config['DEBUG'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        super(TestCase, self).setUp()
        db.create_all()

    def tearDown(self):
        db.drop_all()
        super(TestCase, self).tearDown()
