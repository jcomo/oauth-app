from flask import url_for

from tests.test_case import TestCase

from oanalytics.identity.models import User
from oanalytics.identity.routes import sessions


class UserRegistrationTestCase(TestCase):
    def test_renders_registration_form(self):
        response = self.client.get(url_for('identity.register'))
        self.assert200(response)

        html = response.data
        self.assertIn("<title>Register</title>", html)
        self.assertIn("New User", html)
        self.assertIn("Name", html)
        self.assertIn("Username", html)
        self.assertIn("Password", html)
        self.assertIn("Confirm Password", html)

    def test_user_successfully_registers(self):
        data = {
            'name': 'Jonathan Como',
            'username': 'jcomo',
            'password': 'dog',
            'confirm': 'dog'
        }
        response = self.client.post(url_for('identity.register'), data=data)

        self.assertRedirects(response, url_for('analytics.apps'))

        user = User.query.filter_by(username='jcomo').first()
        self.assertIsNotNone(user)

        session_id = self.get_cookie('session_id')
        self.assertIsNotNone(sessions.retrieve(session_id))

    def test_when_user_fails_to_register_does_not_redirect(self):
        data = {
            'name': 'Jonathan Como',
            'username': 'jcomo',
            'password': 'dog',
            'confirm': 'cat'
        }
        response = self.client.post(url_for('identity.register'), data=data)

        self.assertIn("<title>Register</title>", response.data)
        self.assertEqual(0, User.query.count())
        self.assertIsNone(self.get_cookie('session_id'))


class UserLoginTestCase(TestCase):
    def test_renders_login_form(self):
        response = self.client.get(url_for('identity.login'))
        self.assert200(response)

        html = response.data
        self.assertIn("<title>Login</title>", html)
        self.assertIn("Welcome Back", html)
        self.assertIn("Username", html)
        self.assertIn("Password", html)

    def test_logs_in_when_credentials_match(self):
        User.register('Jonathan Como', 'jcomo', 'dog')
        data = {'username': 'jcomo', 'password': 'dog'}
        response = self.client.post(url_for('identity.login'), data=data)

        self.assertRedirects(response, url_for('analytics.apps'))

        session_id = self.get_cookie('session_id')
        self.assertIsNotNone(sessions.retrieve(session_id))

    def test_does_not_login_in_when_credentials_dont_match(self):
        User.register('Jonathan Como', 'jcomo', 'dog')
        data = {'username': 'jcomo', 'password': 'cat'}
        response = self.client.post(url_for('identity.login'), data=data)

        self.assertIn("<title>Login</title>", response.data)
        self.assertIsNone(self.get_cookie('session_id'))


class UserLogoutTestCase(TestCase):
    def test_logging_out_destroys_session(self):
        user = User.register('Jonathan Como', 'jcomo', 'dog')
        session_id = self.login_as(user)

        response = self.client.get(url_for('identity.logout'))

        self.assertRedirects(response, url_for('identity.login'))
        self.assertIsNone(sessions.retrieve(session_id))
        self.assertEqual('', self.get_cookie('session_id'))

    def test_user_is_redirected_when_not_logged_in(self):
        response = self.client.get(url_for('identity.logout'))

        self.assertRedirects(response, url_for('identity.login'))

    def test_user_remains_logged_out_after_logging_out(self):
        # TODO: do this test when routes are authenticated
        pass