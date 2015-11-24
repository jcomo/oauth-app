from flask import url_for

from tests.test_case import TestCase

from oanalytics.identity.models import User


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


class UserLoginTestCase(TestCase):
    def test_logs_in_when_credentials_match(self):
        pass

    def test_does_not_login_in_when_credentials_dont_match(self):
        pass


class UserLogoutTestCase(TestCase):
    def test_user_can_log_out_when_logged_in(self):
        pass

    def test_user_is_redirected_when_not_logged_in(self):
        pass

    def test_user_remains_logged_out_after_logging_out(self):
        pass
