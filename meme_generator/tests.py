from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Meme, MemeTemplate, Rating


class UserSignupViewTest(APITestCase):
    
    def setUp(self):
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

class ReceiveAllTemplatesTest(APITestCase):

    def setUp(self):
        # Create a test user and authenticate
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_TOKEN=self.token.key, HTTP_ID=str(self.user.id))

        # Create sample meme templates
        MemeTemplate.objects.create(name="Template1", image_url="http://example.com/template1.jpg", 
                                    default_top_text="Top Text 1", default_bottom_text="Bottom Text 1")
        MemeTemplate.objects.create(name="Template2", image_url="http://example.com/template2.jpg", 
                                    default_top_text="Top Text 2", default_bottom_text="Bottom Text 2")
        
        # Define the URL for retrieving all templates
        self.url = reverse('receive_all_templates')

    def test_receive_all_templates_success(self):
        """Test successfully retrieving all meme templates."""
        # Send GET request to retrieve all meme templates
        response = self.client.get(self.url)

        # Assert the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response contains 2 templates
        self.assertEqual(len(response.data), 2)

        # Verify the data for each template
        template1 = response.data[0]
        template2 = response.data[1]

        self.assertEqual(template1['name'], 'Template1')
        self.assertEqual(template1['image_url'], 'http://example.com/template1.jpg')
        self.assertEqual(template1['default_top_text'], 'Top Text 1')
        self.assertEqual(template1['default_bottom_text'], 'Bottom Text 1')

        self.assertEqual(template2['name'], 'Template2')
        self.assertEqual(template2['image_url'], 'http://example.com/template2.jpg')
        self.assertEqual(template2['default_top_text'], 'Top Text 2')
        self.assertEqual(template2['default_bottom_text'], 'Bottom Text 2')

    def test_receive_no_templates(self):
        """Test retrieving templates when no templates exist."""
        # Clear the MemeTemplate objects
        MemeTemplate.objects.all().delete()

        # Send GET request to retrieve all meme templates
        response = self.client.get(self.url)

        # Assert that the response contains no templates
        self.assertEqual(len(response.data), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RateMemeViewTestCase(APITestCase):

    def setUp(self):
        # Create a user and authentication token
        self.user = User.objects.create_user(username='testuser', password='password')
        self.token = Token.objects.create(user=self.user)
        
        # Create a meme template
        self.template = MemeTemplate.objects.create(
            name="Funny Template",
            image_url="http://example.com/image.png",
            default_top_text="Default Top",
            default_bottom_text="Default Bottom"
        )
        
        # Create a meme
        self.meme = Meme.objects.create(
            template=self.template,
            top_text="Top text for the meme",
            bottom_text="Bottom text for the meme",
            created_by=self.user
        )
        
        # Prepare the URL and headers for the POST request
        self.meme_id = self.meme.id
        self.rate_meme_url = f'/api/memes/{self.meme_id}/rate/'
        self.headers = {
            'HTTP_Token': f'{self.token.key}',
            'HTTP_Id': str(self.user.id),
        }
        
    def test_rate_meme(self):
        # Prepare the rating data
        data = {
            'score': 5  # Assuming the score is an integer field
        }

        # Make the POST request to rate the meme
        response = self.client.post(self.rate_meme_url, data,**self.headers )
        print(response.data)

        # Check that the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Rating created successfully!')

        # Check that the rating was created correctly
        rating = Rating.objects.get(meme=self.meme, user=self.user)
        self.assertEqual(rating.score, 5)

    def test_rate_meme_update(self):
        # Create an existing rating to simulate an update
        existing_rating = Rating.objects.create(meme=self.meme, user=self.user, score=3)

        # Prepare new rating data
        data = {
            'score': 4  # Update the score
        }

        # Make the POST request to update the rating
        response = self.client.post(self.rate_meme_url, data, **self.headers)

        # Check that the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Rating updated successfully!')

        # Check that the rating was updated
        updated_rating = Rating.objects.get(meme=self.meme, user=self.user)
        self.assertEqual(updated_rating.score, 4)

        # Optionally, you can also check that the old rating is no longer present
        # but since the update logic deletes it, we check only for the updated rating
        self.assertNotEqual(existing_rating.score, updated_rating.score)



class RandomMemeViewTestCase(APITestCase):

    def setUp(self):
        # Create a user and authentication token
        self.user = User.objects.create_user(username='testuser', password='password')
        self.token = Token.objects.create(user=self.user)
        
        # Create a meme template
        self.template = MemeTemplate.objects.create(
            name="Funny Template",
            image_url="http://example.com/image.png",
            default_top_text="Default Top",
            default_bottom_text="Default Bottom"
        )
        
        # Create a meme
        self.meme = Meme.objects.create(
            template=self.template,
            top_text="Top text for the meme",
            bottom_text="Bottom text for the meme",
            created_by=self.user
        )
        
        # Prepare the URL and headers for the GET request
        self.random_meme_url = '/api/memes/random/'  # Update the URL according to your routing
        self.headers = {
            'HTTP_Token': f'{self.token.key}',
            'HTTP_Id': str(self.user.id),
        }

    def test_get_random_meme(self):
        # Make the GET request to retrieve a random meme
        response = self.client.get(self.random_meme_url, **self.headers)
        
        # Check that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the response contains the correct meme data
        self.assertIn('template', response.data)
        self.assertIn('top_text', response.data)
        self.assertIn('bottom_text', response.data)
        self.assertEqual(response.data['top_text'], self.meme.top_text)
        self.assertEqual(response.data['bottom_text'], self.meme.bottom_text)

    def test_get_random_meme_no_memes(self):
        # Delete the existing meme to simulate no memes in the database
        Meme.objects.all().delete()

        # Make the GET request to retrieve a random meme
        response = self.client.get(self.random_meme_url, **self.headers)

        # Check that the response indicates no memes found
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'No memes found.')



class TopRatedMemesViewTestCase(APITestCase):


    def setUp(self):
        # Create a user and authentication token
        self.user = User.objects.create_user(username='testuser', password='password')
        user_2 = User.objects.create_user(username='otheruser', password='password')
        self.token = Token.objects.create(user=self.user)

        # Create a meme template
        self.template = MemeTemplate.objects.create(
            name="Funny Template",
            image_url="http://example.com/image.png",
            default_top_text="Default Top",
            default_bottom_text="Default Bottom"
        )

        # Create some memes
        self.meme1 = Meme.objects.create(
            template=self.template,
            top_text="Meme 1",
            bottom_text="Bottom 1",
            created_by=self.user
        )
        self.meme2 = Meme.objects.create(
            template=self.template,
            top_text="Meme 2",
            bottom_text="Bottom 2",
            created_by=self.user
        )

        # Create ratings for the memes
        Rating.objects.create(meme=self.meme1, user=self.user, score=5)  # First rating
        Rating.objects.create(meme=self.meme1, user=user_2, score=4)  # Rating by a different user
        Rating.objects.create(meme=self.meme2, user=self.user, score=3)  # Rating for meme2

        # Prepare the URL and headers for the GET request
        self.top_memes_url = '/api/memes/top/'
        self.headers = {
            'HTTP_Token': f'{self.token.key}',
            'HTTP_Id': str(self.user.id),
        }

    def test_get_top_rated_memes(self):
        # Make the GET request to retrieve top rated memes
        response = self.client.get(self.top_memes_url, **self.headers)

        # Check that the response is successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the response contains the correct number of memes
        self.assertEqual(len(response.data), 2)  # We created 2 memes

        # Verify that the memes are returned with the correct average ratings
        self.assertEqual(response.data[0]['id'], self.meme1.id)
        self.assertAlmostEqual(response.data[0]['avg_rating'], 4.5)  # Average of 5 and 4
        self.assertEqual(response.data[1]['id'], self.meme2.id)
        self.assertAlmostEqual(response.data[1]['avg_rating'], 3.0)  # Single rating of 3

    def test_get_top_rated_memes_no_ratings(self):
        # Clear existing ratings to simulate no ratings for memes
        Rating.objects.all().delete()

        # Make the GET request to retrieve top rated memes
        response = self.client.get(self.top_memes_url, **self.headers)

        # Check that the response indicates no memes with ratings
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])  # Expecting an empty list since there are no ratings
