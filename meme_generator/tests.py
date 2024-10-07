from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Meme, MemeTemplate


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


class MemeViewTest(APITestCase):

    def setUp(self):
        # Create a test user and token for authentication
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)

        # Create a meme template for use in tests
        self.template = MemeTemplate.objects.create(
            name="Test Template",
            default_top_text="Default Top",
            default_bottom_text="Default Bottom"
        )

        # Set URL for the memes API
        self.meme_url = reverse('meme_request')

    def test_create_meme_success(self):
        """Test that a meme can be created successfully."""
        data = {
            'template': self.template.id,
            'top_text': 'Custom Top Text',
            'bottom_text': 'Custom Bottom Text'
        }
        headers = {
            'HTTP_TOKEN': self.token.key,
            'HTTP_ID': str(self.user.id)
        }

        response = self.client.post(self.meme_url, data, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['message'], 'Meme created successfully!')

    def test_create_meme_missing_auth(self):
        """Test that creating a meme fails when authentication headers are missing."""
        data = {
            'template': self.template.id,
            'top_text': 'Custom Top Text',
            'bottom_text': 'Custom Bottom Text'
        }

        response = self.client.post(self.meme_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Token or user_id missing', response.data['non_field_errors'])
    
    def test_create_meme_invalid_template(self):
        """Test that creating a meme fails if the template does not exist."""
        data = {
            'template': 999,  # Invalid template ID
            'top_text': 'Custom Top Text',
            'bottom_text': 'Custom Bottom Text'
        }
        headers = {
            'HTTP_TOKEN': self.token.key,
            'HTTP_ID': str(self.user.id)
        }

        response = self.client.post(self.meme_url, data, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('template', response.data)

    def test_get_memes_success(self):
        """Test that memes can be retrieved successfully with pagination."""
        # Create a meme to test retrieval
        Meme.objects.create(
            template=self.template,
            top_text='Custom Top Text',
            bottom_text='Custom Bottom Text',
            created_by=self.user
        )

        headers = {
            'HTTP_TOKEN': self.token.key,
            'HTTP_ID': str(self.user.id)
        }

        response = self.client.get(self.meme_url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_get_memes_missing_auth(self):
        """Test that retrieving memes fails when authentication headers are missing."""
        
        response = self.client.get(self.meme_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Token or user_id missing', response.data['non_field_errors'])

class CreateMemeTemplateTest(APITestCase):
    def setUp(self):
        # Create a test user and authenticate
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_TOKEN=self.token.key, HTTP_ID=str(self.user.id))

        # Define the URL for the meme template creation
        self.url = reverse('create_meme_template')

    def test_create_meme_template_success(self):
        """Test creating a meme template successfully."""
        data = {
            "name": "Funny Meme Template",
            "image_url": "http://example.com/meme.jpg",
            "default_top_text": "Top Text",
            "default_bottom_text": "Bottom Text"
        }

        # Send POST request to create a meme template
        response = self.client.post(self.url, data)

        # Assert that the response status code is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the meme template was created in the database
        meme_template = MemeTemplate.objects.get(name="Funny Meme Template")
        self.assertIsNotNone(meme_template)
        self.assertEqual(meme_template.name, data['name'])

    def test_create_meme_template_invalid_data(self):
        """Test creating a meme template with invalid data."""
        data = {
            "name": "",
            "image_url": "http://example.com/meme.jpg"
        }

        # Send POST request with invalid data
        response = self.client.post(self.url, data)

        # Assert that the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the errors are returned in the response
        self.assertIn('name', response.data)


class RetrieveMemeTest(APITestCase):
    def setUp(self):
        # Create a test user and authenticate
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_TOKEN=self.token.key, HTTP_ID=str(self.user.id))

        # Create a meme template
        self.meme_template = MemeTemplate.objects.create(name="Template1", image_url="http://example.com/template.jpg")

        # Create a meme
        self.meme = Meme.objects.create(
            template=self.meme_template,
            top_text="Top",
            bottom_text="Bottom",
            created_by=self.user
        )

        # Define the URL for retrieving the specific meme
        self.url = reverse('retrieve_meme', kwargs={'meme_id': self.meme.id})

    def test_retrieve_meme_success(self):
        """Test successfully retrieving a meme."""
        # Send GET request to retrieve the meme
        response = self.client.get(self.url)

        # Assert that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the returned data matches the meme's fields
        self.assertEqual(response.data['id'], self.meme.id)
        self.assertEqual(response.data['top_text'], self.meme.top_text)
        self.assertEqual(response.data['bottom_text'], self.meme.bottom_text)
        self.assertEqual(response.data['template_id'], self.meme.template.id)

    def test_retrieve_meme_not_found(self):
        """Test retrieving a non-existing meme returns 404."""
        # Define a URL with a non-existent meme_id
        invalid_url = reverse('retrieve_meme', kwargs={'meme_id': 9999})

        # Send GET request with invalid meme_id
        response = self.client.get(invalid_url)

        # Assert that the response status code is 404 Not Found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert that the response contains the appropriate error message
        self.assertEqual(response.data['error'], 'Meme not found.')