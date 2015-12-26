from flask import url_for

from tests.test_case import TestCase
from tests.identity.auth_mixin import AuthTestMixin

from app.oauth.models import OAuthApplication, OAuthGrant
from app.identity.models import User


class OAuthAuthorizationTestCase(TestCase, AuthTestMixin):
    def setUp(self):
        super(OAuthAuthorizationTestCase, self).setUp()
        self.developer = User.register('Joe Dev', 'jdev', 'cat')
        self.application = OAuthApplication(self.developer, 'Test App', 'http://example.com')

        user = User.register('Jonathan Como', 'jcomo', 'dog')
        self.login_as(user)

    def test_redirects_resource_owner_to_login_when_not_logged_in(self):
        self.client.get(url_for('identity.logout'))
        query = {'client_id': 'abc', 'response_type': 'code'}
        response = self.client.get(url_for('oauth.authorize'), query_string=query)

        auth_url = url_for('oauth.authorize', client_id='abc', response_type='code', _external=True)
        self.assertRedirects(response, url_for('identity.login', next=auth_url))

    def test_prompts_resource_owner_for_scopes(self):
        auth_query = {'client_id': self.application.client_id, 'response_type': 'code', 'scopes': 'read_analytics'}
        response = self.client.get(url_for('oauth.authorize'), query_string=auth_query)
        self.assert200(response)

        html = response.data
        title = "<title>Authorize %s</title>" % self.application.name
        self.assertIn(title, html)
        self.assertIn("Read analytics data", html)

    def test_responds_with_error_when_no_application_for_client_id(self):
        auth_query = {'client_id': 'abc', 'response_type': 'code'}
        response = self.client.get(url_for('oauth.authorize'), query_string=auth_query)

        self.assert401(response)
        self.assertEqual(response.json, {'error': 'invalid_client'})

    def test_responds_with_error_when_specified_scopes_are_invalid(self):
        auth_query = {
            'response_type': 'code',
            'client_id': self.application.client_id,
            'scopes': 'read_public_profile|malicious_scope'
        }

        response = self.client.get(url_for('oauth.authorize'), query_string=auth_query)

        self.assert400(response)
        self.assertEqual(response.json, {'error': 'invalid_scope'})

    def test_responds_with_error_when_missing_required_parameters(self):
        auth_query = {
            'client_id': self.application.client_id,
            'scopes': 'read_public_profile'
        }

        response = self.client.get(url_for('oauth.authorize'), query_string=auth_query)

        self.assert400(response)
        self.assertEqual(response.json, {'error': 'invalid_request'})
