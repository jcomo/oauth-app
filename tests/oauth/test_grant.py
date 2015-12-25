from flask import url_for

from tests.test_case import TestCase
from tests.identity.auth_mixin import AuthTestMixin

from app.oauth.models import OAuthApplication, OAuthGrant
from app.identity.models import User


class OAuthGrantTestCase(TestCase, AuthTestMixin):
    def setUp(self):
        super(OAuthGrantTestCase, self).setUp()
        developer = User.register('Joe Dev', 'jdev', 'cat')
        self.application = OAuthApplication(developer, 'Test App', 'http://example.com')

        self.user = User.register('Jonathan Como', 'jcomo', 'dog')
        self.login_as(self.user)

    def test_redirects_to_application_redirect_uri_when_scopes_accepted(self):
        grant_data = {'client_id': self.application.client_id, 'response_type': 'code', 'scopes': 'read_analytics'}
        response = self.client.post(url_for('oauth.authorize'), data=grant_data)

        grant = self.application.grants.first()
        self.assertIsNotNone(grant)
        self.assertEqual(grant.user, self.user)

        redirect_uri = 'http://example.com?code=' + grant.code
        self.assertIn(response.status_code, (301, 302))
        self.assertEqual(response.location, redirect_uri)

    def test_responds_with_error_when_no_application_for_client_id(self):
        grant_data = {'client_id': 'abc', 'response_type': 'code', 'scopes': 'read_public_profile'}
        response = self.client.post(url_for('oauth.authorize'), data=grant_data)

        self.assert401(response)
        self.assertEqual(response.json, {'error': 'invalid_client'})

    def test_responds_with_error_when_specified_scopes_are_invalid(self):
        grant_data = {
            'response_type': 'code',
            'client_id': self.application.client_id,
            'scopes': 'read_public_profile|malicious_scope'
        }

        response = self.client.post(url_for('oauth.authorize'), data=grant_data)

        self.assert400(response)
        self.assertEqual(response.json, {'error': 'invalid_scopes'})

    def test_responds_with_error_when_missing_required_parameters(self):
        grant_data = {
            'client_id': self.application.client_id,
            'scopes': 'read_public_profile'
        }

        response = self.client.post(url_for('oauth.authorize'), data=grant_data)

        self.assert400(response)
        self.assertEqual(response.json, {'error': 'invalid_request'})
