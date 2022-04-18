from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.authtoken.models import Token
from tracker.models import User

# initialize the APIClient app
client = Client()


class UnauthorizedUserTest(TestCase):
    """
    Try to access any api endpoint while unauthorized
    """
    def test_access_unauthorized(self):
        response = client.get(reverse('item-list'), format='json')
        self.assertEqual(response.data['detail'].title(), 'Authentication Credentials Were Not Provided.')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SessionAuthTest(TestCase):
    """
    Test session auth
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@gmail.com',
            password='test'
        )

    def test_valid_credentials_session_auth(self):
        self.assertTrue(client.login(email='test@gmail.com', password='test'))

    def test_invalid_credentials_session_auth(self):
        self.assertFalse(client.login(email='test@gmail.com'))
        self.assertFalse(client.login(email='test@gmail.com', password='wrong'))
        self.assertFalse(client.login(email='wrong', password='tt'))


class GetTokenTest(TestCase):
    """
    Test GET token
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@gmail.com',
            password='test'
        )

    def test_get_token_with_missing_password(self):
        auth_data = {
            'email': 'test@gmail.com',
        }
        auth_response = client.post(reverse('token-auth'), data=auth_data)
        self.assertEqual(auth_response.data['password'][0].title(), 'This Field Is Required.')
        self.assertEqual(auth_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_token_with_missing_email(self):
        auth_data = {
            'password': 'test',
        }
        auth_response = client.post(reverse('token-auth'), data=auth_data)
        self.assertEqual(auth_response.data['email'][0].title(), 'This Field Is Required.')
        self.assertEqual(auth_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_token_with_invalid_email_address(self):
        auth_data = {
            'email': 'wrong',
            'password': 'test',
        }
        auth_response = client.post(reverse('token-auth'), data=auth_data)
        self.assertEqual(auth_response.data['email'][0].title(), 'Enter A Valid Email Address.')
        self.assertEqual(auth_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_token_with_invalid_password(self):
        auth_data = {
            'email': 'test@gmail.com',
            'password': 'wrong',
        }
        auth_response = client.post(reverse('token-auth'), data=auth_data)
        self.assertEqual(auth_response.data['non_field_errors'][0].title(),
                         'Unable To Log In With Provided Credentials.')
        self.assertEqual(auth_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_token_with_valid_credentials(self):
        auth_data = {
            'email': 'test@gmail.com',
            'password': 'test',
        }
        auth_response = client.post(reverse('token-auth'), data=auth_data)
        token_from_response = auth_response.json()['token']
        token_from_db = Token.objects.get(user=self.user).key
        self.assertEqual(token_from_response, token_from_db)


class AccessWithTokenTest(TestCase):
    """
    Test having access to api endpoint with token
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@gmail.com',
            password='test'
        )

    def test_try_access_with_token(self):
        token = Token.objects.create(user=self.user)
        response = client.get(reverse('item-list'), format='json', **{'HTTP_AUTHORIZATION': f'Token {token}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_try_access_with_wrong_token(self):
        token = 'aafd'
        response = client.get(reverse('item-list'), format='json', **{'HTTP_AUTHORIZATION': f'Token {token}'})
        self.assertEqual(response.data['detail'].title(), 'Invalid Token.')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
