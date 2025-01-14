from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Profile


class AuthAPITests(APITestCase):

    def setUp(self):
        # Setup initial data for testing
        self.valid_user_data = {
            "username": "testuser",
            "password": "password123",
            "email": "testuser@example.com",
            "phone_number": "1234567890",
            "role": "Public"
        }
        self.valid_user_data_1 = {
            "username": "testuser1",
            "password": "password123",
            "email": "testuser1@example.com",
            "phone_number": "1234567890",
            "role": "Public"
        }
        
        self.invalid_user_data = {
            "username": "testuser2",
            "password": "password123",
            "email": "testuser2@example.com",
            "role": "NonExistentRole"  # Invalid role
        }

        self.login_data = {
            "username": "testuser",
            "password": "password123"
        }
        
        self.create_user(self.valid_user_data)

    def create_user(self, user_data):
        """Helper method to create a user"""
        response = self.client.post('/api/register/', user_data)
        return response

    def test_register_user(self):
        """Test the user registration API"""
        response = self.create_user(self.valid_user_data_1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual('User registered successfully',response.data['message'])

    def test_register_user_with_invalid_data(self):
        """Test registration with invalid data (invalid role)"""
        response = self.client.post('/api/register/', self.invalid_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)

    def test_login_user(self):
        """Test login with valid credentials"""
        response = self.client.post('/api/login/', self.login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Login successful', response.data['message'])

    def test_login_user_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        invalid_login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post('/api/login/', invalid_login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_login_user_with_inactive_account(self):
        """Test login with an inactive user account"""
        user = User.objects.create_user(username="inactiveuser", password="password123", email="inactive@example.com")
        user.is_active = False
        user.save()

        login_data = {
            "username": "inactiveuser",
            "password": "password123"
        }
        response = self.client.post('/api/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_register_user_missing_fields(self):
        """Test registration with missing required fields"""
        incomplete_data = {
            "password": "password123"
        }
        response = self.client.post('/api/register/', incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['username'][0], 'This field is required.')

class ProfileAPITests(APITestCase):

    def setUp(self):
        # Use the registration API to create a user and profile
        self.register_url = "/api/register/"
        self.login_url = "/api/login/"
        self.profile_url = "/api/profile/"
        self.edit_profile_url = "/api/edit_profile/"

        self.valid_user_data = {
            "username": "testuser",
            "password": "password123",
            "email": "test@example.com",
            "phone_number": "1234567890",
            "role": "Public"
        }

        # Register the user via the API
        response = self.client.post(self.register_url, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve the user and profile for further tests
        self.user = User.objects.get(username="testuser")
        self.profile = self.user.profile

        # Force login for tests requiring authentication
        self.client.force_login(self.user)

        # Register another user for testing profile visibility
        self.other_user_data = {
            "username": "otheruser",
            "password": "password123",
            "email": "other@example.com",
            "phone_number": "9876543210",
            "role": "Low-Income User"
        }
        response = self.client.post(self.register_url, self.other_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.other_user = User.objects.get(username="otheruser")
        self.other_profile = self.other_user.profile
        self.other_profile_url = "/api/profile/otheruser/"

    def test_profile_creation_on_user_registration(self):
        """Ensure a Profile is created when a User is registered via the API"""
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.role, "Public")
        self.assertEqual(self.profile.phone_number, "1234567890")
        self.assertEqual(self.profile.user.email, "test@example.com")

    def test_retrieve_own_profile(self):
        """Test retrieving the logged-in user's profile"""
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['role'], self.profile.role)

    def test_edit_own_profile(self):
        """Test editing the logged-in user's profile"""
        updated_data = {
            "phone_number": "9876543210",
            "is_phone_public": False,
            "role": "Organisation",
            "bio": "Updated bio",
            "is_dm_open": False
        }
        response = self.client.put(self.edit_profile_url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the profile was updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.phone_number, "9876543210")
        self.assertFalse(self.profile.is_phone_public)
        self.assertEqual(self.profile.role, "Organisation")
        self.assertEqual(self.profile.bio, "Updated bio")
        self.assertFalse(self.profile.is_dm_open)
    def test_retrieve_profile_without_authentication(self):
        """Test retrieving own (no username in url) profile without being logged in"""
        self.client.logout()  # Log out the user
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_profile_without_authentication(self):
        """Test editing user profile without being logged in"""
        self.client.logout()  # Log out the user
        updated_data = {
            "phone_number": "9876543210"
        }
        response = self.client.put(self.edit_profile_url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_profile_edit(self):
        """Test editing a profile with invalid data"""
        updated_data = {
            "phone_number": "invalid_number"  # Invalid format
        }
        response = self.client.put(self.edit_profile_url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone_number", response.data)

    def test_view_other_user_profile(self):
        """Ensure that anyone can view another user's profile"""
        response = self.client.get(self.other_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the profile data for the other user
        self.assertEqual(response.data['username'], self.other_user.username)
        self.assertEqual(response.data['role'], self.other_profile.role)

    def test_view_other_user_profile_not_logged_in(self):
        """Ensure that logged-out users can view other profiles"""
        self.client.logout()
        response = self.client.get(self.other_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate profile data
        self.assertEqual(response.data['username'], self.other_user.username)
        self.assertEqual(response.data['role'], self.other_profile.role)

    def test_edit_other_user_profile_not_logged_in(self):
        """Test that a logged-out user cannot edit any profile"""
        self.client.logout()  # Ensure the client is logged out

        updated_data = {
            "phone_number": "9876543210",
            "role": "Organisation"
        }
        response = self.client.put(self.edit_profile_url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_phone_number_visible_to_profile_owner(self):
        """Ensure the phone number is visible to the profile owner."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('phone_number', response.data)
        self.assertEqual(response.data['phone_number'], self.profile.phone_number)

    def test_phone_number_hidden_if_not_public(self):
        """Ensure the phone number is hidden for non-owners when is_phone_public is False."""
        self.other_profile.is_phone_public = False
        self.other_profile.save()

        response = self.client.get(self.other_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('phone_number', response.data)
        self.client.logout()

        response = self.client.get(self.other_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('phone_number', response.data)

    def test_phone_number_visible_if_public(self):
        """Ensure the phone number is visible for non-owners when is_phone_public is True."""
        self.other_profile.is_phone_public = True
        self.other_profile.save()

        response = self.client.get(self.other_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('phone_number', response.data)
        self.assertEqual(response.data['phone_number'], self.other_profile.phone_number)

        self.client.logout()

        response = self.client.get(self.other_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('phone_number', response.data)
        self.assertEqual(response.data['phone_number'], self.other_profile.phone_number)
        
        
