from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

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

    # def test_user_signup_duplicate_username(self):
    #     """Test that signing up fails if the username is already taken."""
    #     # Create a user beforehand
    #     User.objects.create_user(username='testuser', email='testuser@example.com', password='strongpassword')

    #     data = {
    #         'username': 'testuser',  # Same username
    #         'email': 'newuser@example.com',
    #         'password': 'strongpassword'
    #     }
    #     response = self.client.post(self.signup_url, data)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('username', response.data)

    # def test_user_signup_duplicate_email(self):
    #     """Test that signing up fails if the email is already taken."""
    #     # Create a user beforehand
    #     User.objects.create_user(username='uniqueuser', email='testuser@example.com', password='strongpassword')

    #     data = {
    #         'username': 'newuser',
    #         'email': 'testuser@example.com',  # Same email
    #         'password': 'strongpassword'
    #     }
    #     response = self.client.post(self.signup_url, data)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('email', response.data)
