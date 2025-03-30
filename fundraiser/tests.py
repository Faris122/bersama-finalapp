from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import *
from account.models import *

class GetCreateTestCase(APITestCase):
    def setUp(self):
        # Test Public Users
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user_profile = Profile.objects.create(user=self.user, role='Public', needs_help=True)
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword')
        self.user2_profile = Profile.objects.create(user=self.user2, role='Public', needs_help=True)

        # Test Organisations
        self.org_user = User.objects.create_user(username='testorg', password='testpassword')
        self.org_profile = Profile.objects.create(user=self.org_user, role='Organisation')

        # Test Fundraisers
        self.fundraiser = Fundraiser.objects.create(
            user=self.user,
            title="Test Fundraiser",
            description="This is a test fundraiser.",
            goal_amount=1000.00,
            end_date="2029-12-31T23:59:59Z"
        )

        # Test Donation
        self.donation = Payment.objects.create(
            user=self.user,
            fundraiser=self.fundraiser,
            amount=100.00,
            message="Test donation"
        )

        # Test Expired Fundraiser
        self.fundraiser_old = Fundraiser.objects.create(
            user=self.org_user,
            title="Test Fundraiser",
            description="This is a test fundraiser.",
            goal_amount=1000.00,
            end_date="2022-12-31T23:59:59Z"
        )


    def test_get_all_fundraisers(self):
        """Test to get all fundraisers in a list."""
        url = '/api/fundraisers/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) 

    def test_get_fundraiser_detail(self):
        """Test to get individual fundraiser details."""
        url = f'/api/fundraisers/{str(self.fundraiser.id)}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], "This is a test fundraiser.")

    def test_get_fundraiser_detail_invalid(self):
        url = f'/api/fundraisers/9999/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_fundraiser(self):
        """Test to create a new fundraiser."""
        self.client.force_login(self.user2)
        url = '/api/fundraisers/create/'
        data = {
            "title": "New Fundraiser",
            "description": "This is a new fundraiser.",
            "goal_amount": 2000.00,
            "end_date": "2023-12-31T23:59:59Z"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Fundraiser.objects.count(), 3)

    def test_create_fundraiser_user_already_created(self):
        """Make sure Public users only create one fundraiser"""
        self.client.force_login(self.user)
        url = '/api/fundraisers/create/'
        data = {
            "title": "New Fundraiser",
            "description": "This is a new fundraiser.",
            "goal_amount": 2000.00,
            "end_date": "2023-12-31T23:59:59Z"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Fundraiser.objects.count(), 2)

    def test_create_fundraiser_unauthenticated(self):
        """Make sure unauthenticated users could not create fundraisers. """
        self.client.logout()
        url = '/api/fundraisers/create/'
        data = {
            "title": "New Fundraiser",
            "description": "This is a new fundraiser.",
            "goal_amount": 2000.00,
            "end_date": "2023-12-31T23:59:59Z"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_donation(self):
        """Create a new donation."""
        url = '/api/donations/create/'
        data = {
            "fundraiser": self.fundraiser.id,
            "amount": 50.00,
            "message": "Another test donation",
            "anon_name": "Anonymous Donor" 
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 2)

    def test_create_donation_after_fundraiser_end(self):
        """Test to make sure no new donations after fundraiser end."""
        url = '/api/donations/create/'
        data = {
            "fundraiser": self.fundraiser_old.id,
            "amount": 50.00,
            "message": "Another test donation",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.count(), 1)

    def test_get_user_donations(self):
        """Get all donations from a user."""
        url = '/api/donations/user/' + self.user.username +'/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one donation exists for this user

    def test_create_fundraiser_as_organisation(self):
        """Create more than one fundraiser as an organisation."""
        self.client.force_login(self.org_user)  # Authenticate the organisation user
        url = '/api/fundraisers/create/'
        data_1 = {
            "title": "Organisation Fundraiser",
            "description": "This is a fundraiser by an organisation.",
            "goal_amount": 5000.00,
            "end_date": "2029-12-31T23:59:59Z"
        }
        response_1 = self.client.post(url, data_1, format='json')
        data = {
            "title": "Organisation Fundraiser 2",
            "description": "This is a fundraiser by an organisation.",
            "goal_amount": 5000.00,
            "end_date": "2029-12-31T23:59:59Z"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Fundraiser.objects.count(), 4)

    def test_create_fundraiser_as_user_without_help(self):
        """Test to not allow public users (needs_help=false) to create fundraiser"""
        self.user_profile.needs_help = False
        self.user_profile.save()
        self.client.force_login(self.user)
        url = '/api/fundraisers/create/'
        data = {
            "title": "Invalid Fundraiser",
            "description": "This should not be allowed.",
            "goal_amount": 1000.00,
            "end_date": "2029-12-31T23:59:59Z"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # User without needs_help cannot create fundraisers
        self.assertEqual(Fundraiser.objects.count(), 2)  # Only one fundraiser exists

class CommentTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user_profile = Profile.objects.create(user=self.user, role='Public', needs_help=True)
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.otheruser_profile = Profile.objects.create(user=self.other_user, role='Public', needs_help=True)

        self.fundraiser = Fundraiser.objects.create(
            user=self.user,
            title="Test Fundraiser",
            description="This is a test fundraiser.",
            goal_amount=1000.00,
            end_date="2029-12-31T23:59:59Z"
        )
        self.comment = FundraiserComment.objects.create(
            post=self.fundraiser,
            content="This is a test comment.",
            author=self.user
        )
        self.client.force_login(self.user)

    def test_add_comment_logged_in(self):
        response = self.client.post(f'/api/fundraisers/{self.fundraiser.id}/add_comment/', {
            'content': 'This is a test comment.'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a test comment.')

    def test_add_comment_logged_out(self):
        self.client.logout()
        response = self.client.post(f'/api/fundraisers/{self.fundraiser.id}/add_comment/', {
            'content': 'This is a test comment.'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reply_to_comment_with_valid_id(self):
        """Test replying to a comment with a valid parent ID."""
        url = f'/api/fundraisers/{self.fundraiser.id}/add_comment/'
        response = self.client.post(url, {
            'content': 'This is a reply.',
            'parent_id': self.comment.id,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a reply.')
        self.assertEqual(response.data['parent'], self.comment.id)

    def test_reply_to_comment_with_invalid_id(self):
        """Test replying to a comment with an invalid parent ID."""
        url = f'/api/fundraisers/{self.fundraiser.id}/add_comment/'
        response = self.client.post(url, {
            'content': 'This is a reply.',
            'parent_id': 999,  # Non-existent comment ID
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Parent comment not found')

    def test_delete_comment_by_author(self):
        """Test that the author can delete their own comment."""
        url = f'/api/fundraisers/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Comment deleted successfully')
        self.assertFalse(FundraiserComment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_by_other_user(self):
        """Test that a non-author cannot delete someone else's comment."""
        self.client.force_login(self.other_user)  # Log in as another user
        url = f'/api/fundraisers/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Permission denied')
        self.assertTrue(FundraiserComment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_unauthenticated(self):
        """Test that an unauthenticated user cannot delete a comment."""
        self.client.logout()  # Log out the user
        url = f'/api/fundraisers/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(FundraiserComment.objects.filter(id=self.comment.id).exists())

    def test_delete_nonexistent_comment(self):
        """Test deleting a comment that does not exist."""
        url = '/api/fundraisers/comments/999/delete/'  # Assuming 999 is an invalid ID
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Comment not found')