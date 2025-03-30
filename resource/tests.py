from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import *

# Create your tests here.

class ResourceListTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = ResourceCategory.objects.create(name='General')
        self.category2 = ResourceCategory.objects.create(name='Help')
        self.resource = Resource.objects.create(
            title="Test Resource",
            content="This is a test resource.",
            author=self.user
        )
        self.resource.categories.add(self.category)
        self.bursary = Bursary.objects.create(
            title="Test Bursary",
            content="This is a test bursary.",
            author=self.user
        )
        self.client.force_login(self.user)

    def test_get_resource_list(self):
        response = self.client.get('/api/resources/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_bursary_list(self):
        response = self.client.get('/api/bursaries/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class ResourceCreateDeleteTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.category = ResourceCategory.objects.create(name='General')
        self.category2 = ResourceCategory.objects.create(name='Help')
        self.resource = Resource.objects.create(
            title="Test Resource",
            content="This is a test resource.",
            author=self.user
        )
        self.resource.categories.add(self.category)
        self.client.force_login(self.user)

    def test_create_resource(self):
        """Test creating a new resource."""
        url = '/api/resources/create/'
        data = {
            'title': 'New Resource',
            'content': 'This is a new resource.',
            'categories': [self.category.id, self.category2.id]  # Use category IDs
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Resource created successfully!')

        resource = Resource.objects.get(title='New Resource')
        self.assertEqual(resource.content, 'This is a new resource.')
        self.assertEqual(resource.author.username, 'testuser')
        self.assertEqual(list(resource.categories.all()), [self.category, self.category2])

    def test_create_resource_unauthenticated(self):
        """Test creating a resource without authentication."""
        self.client.logout()
        url = '/api/resources/create/'
        data = {
            'title': 'Test Resource',
            'content': 'This is a test resource.',
            'categories': [self.category.id]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_resource_by_author(self):
        """Test that the author can delete their own resource."""
        url = f'/api/resources/{self.resource.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Resource deleted successfully')
        self.assertFalse(Resource.objects.filter(id=self.resource.id).exists())

    def test_delete_resource_by_other_user(self):
        """Test that a non-author cannot delete someone else's resource."""
        self.client.force_login(self.other_user)  # Log in as another user
        url = f'/api/resources/{self.resource.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Permission denied')
        self.assertTrue(Resource.objects.filter(id=self.resource.id).exists())

    def test_delete_resource_unauthenticated(self):
        """Test that an unauthenticated user cannot delete a resource."""
        self.client.logout()  # Log out the user
        url = f'/api/resources/{self.resource.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Resource.objects.filter(id=self.resource.id).exists())

    def test_delete_nonexistent_resource(self):
        """Test deleting a resource that does not exist."""
        url = '/api/resources/999/delete/'  # Assuming 999 is an invalid ID
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Resource not found')

class ResourceCommentTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.resource = Resource.objects.create(
            title="Test Resource",
            content="This is a test resource.",
            author=self.user
        )
        self.comment = ResourceComment.objects.create(
            post=self.resource,
            content="This is a test comment.",
            author=self.user
        )
        self.client.force_login(self.user)

    def test_add_comment_logged_in(self):
        response = self.client.post(f'/api/resources/{self.resource.id}/add_comment/', {
            'content': 'This is a test comment.'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a test comment.')

    def test_add_comment_logged_out(self):
        self.client.logout()
        response = self.client.post(f'/api/resources/{self.resource.id}/add_comment/', {
            'content': 'This is a test comment.'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reply_to_comment_with_valid_id(self):
        """Test replying to a comment with a valid parent ID."""
        url = f'/api/resources/{self.resource.id}/add_comment/'
        response = self.client.post(url, {
            'content': 'This is a reply.',
            'parent_id': self.comment.id,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a reply.')
        self.assertEqual(response.data['parent'], self.comment.id)

    def test_reply_to_comment_with_invalid_id(self):
        """Test replying to a comment with an invalid parent ID."""
        url = f'/api/resources/{self.resource.id}/add_comment/'
        response = self.client.post(url, {
            'content': 'This is a reply.',
            'parent_id': 999,  # Non-existent comment ID
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Parent comment not found')

    def test_delete_comment_by_author(self):
        """Test that the author can delete their own comment."""
        url = f'/api/resources/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Comment deleted successfully')
        self.assertFalse(ResourceComment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_by_other_user(self):
        """Test that a non-author cannot delete someone else's comment."""
        self.client.force_login(self.other_user)  # Log in as another user
        url = f'/api/resources/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Permission denied')
        self.assertTrue(ResourceComment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_unauthenticated(self):
        """Test that an unauthenticated user cannot delete a comment."""
        self.client.logout()  # Log out the user
        url = f'/api/resources/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ResourceComment.objects.filter(id=self.comment.id).exists())

    def test_delete_nonexistent_comment(self):
        """Test deleting a comment that does not exist."""
        url = '/api/resources/comments/999/delete/'  # Assuming 999 is an invalid ID
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Comment not found')

class CategoryTestCase(APITestCase):
    def setUp(self):
        ResourceCategory.objects.create(name="General")
        ResourceCategory.objects.create(name="Specific")

    def test_list_categories(self):
        response = self.client.get('/api/resources/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "General")

# All tests below are for the filter and query
class ResourceSearchTestCase(APITestCase):

    def setUp(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        category1 = ResourceCategory.objects.create(name="General")
        category2 = ResourceCategory.objects.create(name="Specific")
        category3 = ResourceCategory.objects.create(name="Help")

        resource1 = Resource.objects.create(
            title="Resource One",
            content="Resource Details",
            author=user
        )
        resource1.categories.add(category1, category3)

        resource2 = Resource.objects.create(
            title="Resource Two",
            content="Resource Details",
            author=user
        )
        resource2.categories.add(category2)

    def test_filter_search_title(self):
        response = self.client.get('/api/resources/search/?q=One')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Resource One")

    def test_filter_search_contents(self):
        response = self.client.get('/api/resources/search/?q=Details')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['content'], "Resource Details")
        
    def test_filter_no_match(self):
        response = self.client.get('/api/resources/search/?q=invalid')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_filter_categories(self):
        response = self.client.get('/api/resources/search/?categories=General,Help')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Resource One")

    def test_filter_categories_no_match(self):
        response = self.client.get('/api/resources/search/?categories=Specific,Help')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

# All tests below are for the filter and query
class BursarySearchTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username="testuser", password="testpass")

        bursary1 = Bursary.objects.create(
            title="Bursary One",
            content="Bursary Details",
            author=user,
            level="primary"
        )

        bursary2 = Bursary.objects.create(
            title="Bursary Two",
            content="Bursary Details",
            author=user,
            level="secondary"
        )

    def test_filter_search_title(self):
        response = self.client.get('/api/bursaries/search/?q=One')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Bursary One")

    def test_filter_search_contents(self):
        response = self.client.get('/api/bursaries/search/?q=Details')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['content'], "Bursary Details")
        
    def test_filter_no_match(self):
        response = self.client.get('/api/bursaries/search/?q=invalid')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_filter_levels(self):
        response = self.client.get('/api/bursaries/search/?levels=primary')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only the Python Tips resource should be returned
        self.assertEqual(response.data[0]['title'], "Bursary One")

    def test_filter_levels_no_match(self):
        response = self.client.get('/api/resources/search/?levels=tertiary')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)