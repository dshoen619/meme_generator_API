from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class UserSignupViewTest(APITestCase):
    
    def setUp(self):
        # Any setup before running the tests can be done here
        self.signup_url = reverse('signup')

    def test_user_signup_success(self):
        """Test that a user can sign up with valid data."""
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'strongpassword'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'], 'testuser')
        
        # Check if the user exists in the database
        user_exists = User.objects.filter(username='testuser').exists()
        self.assertTrue(user_exists)

    def test_user_signup_missing_fields(self):
        """Test that signing up fails if any required field is missing."""
        data = {
            'username': 'testuser',
            # Missing email and password
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)

    def test_user_signup_duplicate_username(self):
        """Test that signing up fails if the username is already taken."""
        # Create a user beforehand
        User.objects.create_user(username='testuser', email='testuser@example.com', password='strongpassword')

        data = {
            'username': 'testuser',  # Same username
            'email': 'newuser@example.com',
            'password': 'strongpassword'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_signup_duplicate_email(self):
        """Test that signing up fails if the email is already taken."""
        # Create a user beforehand
        User.objects.create_user(username='uniqueuser', email='testuser@example.com', password='strongpassword')

        data = {
            'username': 'newuser',
            'email': 'testuser@example.com',  # Same email
            'password': 'strongpassword'
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class UserLoginViewTest(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.login_url = reverse('login')

    def test_user_login_success(self):
        """Test user can log in with valid credentials."""
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['token'], self.token.key)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], f"Welcome {self.user.username}")

    def test_user_login_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'][0], "Invalid credentials")

    def test_user_login_missing_fields(self):
        """Test login fails if any required fields are missing."""
        data = {
            'username': 'testuser'
            # Missing password
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('password', response.data)

        data = {
            'password': 'testpassword'
            # Missing username
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('username', response.data)


class UserLogoutViewTest(APITestCase):
    
    def setUp(self):
        # Create a test user and token
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.logout_url = reverse('logout')

    def test_user_logout_success(self):
        """Test that a user can log out successfully."""
        data = {
            'username': 'testuser'
        }
        response = self.client.post(self.logout_url, data, HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], f"Successfully logged out user '{self.user.username}'.")
        
        # Check that the token has been deleted
        token_exists = Token.objects.filter(user=self.user).exists()
        self.assertFalse(token_exists)

    def test_user_logout_invalid_user(self):
        """Test that logging out fails when the user does not exist."""
        data = {
            'username': 'invaliduser'
        }
        response = self.client.post(self.logout_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'][0], "User not found.")

    def test_user_logout_no_token(self):
        """Test that logging out fails if the user has no token."""
        # Manually delete the user's token
        self.token.delete()
        
        data = {
            'username': 'testuser'
        }
        response = self.client.post(self.logout_url, data, HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Token not found for this user.', response.data)
