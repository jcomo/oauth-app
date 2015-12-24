from flask import url_for

from tests.test_case import TestCase

from oanalytics.oauth.models import OAuthApplication
from oanalytics.identity.models import User


class OAuthRegistrationTestCase(TestCase):
    def setUp(self):
        super(OAuthRegistrationTestCase, self).setUp()
        self.user = User.register('Jonathan Como', 'jcomo', 'dog')
        self.login_as(self.user)

    def test_non_logged_in_user_cannot_view_registration(self):
        self.client.get(url_for('identity.logout'))
        response = self.client.get(url_for('oauth.register'))
        next_url = url_for('oauth.register', _external=True)
        self.assertRedirects(response, url_for('identity.login', next=next_url))

    def test_non_logged_in_user_cannot_submit_registration(self):
        self.client.get(url_for('identity.logout'))
        response = self.client.post(url_for('oauth.register'))
        next_url = url_for('oauth.register', _external=True)
        self.assertRedirects(response, url_for('identity.login', next=next_url))

    def test_registration_form_display(self):
        response = self.client.get(url_for('oauth.register'))
        self.assert200(response)

        html = response.data
        self.assertIn("<title>Register Application</title>", html)
        self.assertIn("Application Name", html)
        self.assertIn("Redirect URI", html)
        self.assertIn("Icon URL", html)
        self.assertIn("Website URL", html)

    def test_registration_failure_renders_form_display_with_errors(self):
        # TODO do we even care about errors in this POC?
        data = {'name': 'OAuth application'}
        response = self.client.post(url_for('oauth.register'), data=data)

        self.assertIn("<title>Register Application</title>", response.data)
        self.assertEqual(0, OAuthApplication.query.count())

    def test_registration_successful_redirects_to_application_page(self):
        data = {'name': 'OAuth application', 'redirect_uri': 'http://example.com'}
        response = self.client.post(url_for('oauth.register'), data=data)

        application = OAuthApplication.query.first()
        self.assertRedirects(response, url_for('oauth.application', application_id=application.id))


class OAuthApplicationTestCase(TestCase):
    from unittest import skip

    @skip("remove import")
    def test_non_logged_in_user_cannot_view_application(self):
        pass

    @skip("remove import")
    def test_renders_view_with_application_information(self):
        pass

    @skip("remove import")
    def test_not_found_when_no_application_exists(self):
        pass


class OAuthAuthorizationTestCase(TestCase):
    from unittest import skip

    def setUp(self):
        super(OAuthAuthorizationTestCase, self).setUp()
        self.developer = User.register('Joe Dev', 'jdev', 'cat')
        self.application = OAuthApplication(self.developer, 'Test App', 'http://example.com')

        self.user = User.register('Jonathan Como', 'jcomo', 'dog')
        self.login_as(self.user)

    def test_redirects_resource_owner_to_login_when_not_logged_in(self):
        self.client.get(url_for('identity.logout'))
        query = {'client_id': 'abc', 'response_type': 'code'}
        response = self.client.get(url_for('oauth.authorize'), query_string=query)

        auth_url = url_for('oauth.authorize', client_id='abc', response_type='code', _external=True)
        self.assertRedirects(response, url_for('identity.login', next=auth_url))

    def test_prompts_resource_owner_for_scopes_after_logging_in(self):
        auth_query = {'client_id': self.application.client_id, 'response_type': 'code', 'scopes': 'read_analytics'}
        response = self.client.get(url_for('oauth.authorize'), query_string=auth_query)
        self.assert200(response)

        html = response.data
        title = "<title>Authorize %s</title>" % self.application.name
        self.assertIn(title, html)
        self.assertIn("Read analytics data", html)

    def test_redirects_to_application_redirect_uri_when_scopes_accepted(self):
        auth_data = {'client_id': self.application.client_id, 'response_type': 'code', 'scopes': 'read_analytics'}
        response = self.client.post(url_for('oauth.authorize'), data=auth_data)

        grant = self.application.grants.first()
        self.assertIsNotNone(grant)

        redirect_uri = 'http://example.com?code=' + grant.code
        self.assertIn(response.status_code, (301, 302))
        self.assertEqual(response.location, redirect_uri)

    @skip("Do this test for get and post")
    def test_responds_with_error_when_no_application_for_client_id(self):
        pass

    @skip("Do this test for get and post")
    def test_responds_with_error_when_specified_scopes_are_invalid(self):
        pass

    def test_responds_with_error_when_missing_required_parameters(self):
        pass
