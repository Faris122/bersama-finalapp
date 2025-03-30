from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import *
from account.models import Profile

class ServiceListTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile = Profile.objects.create(user=self.user)
        self.category = ServiceCategory.objects.create(name='Test1')
        self.category2 = ServiceCategory.objects.create(name='Test2')
        self.service = Service.objects.create(
            title="Test Service",
            content="This is a test service.",
        )
        self.service.categories.add(self.category)
        self.client.force_login(self.user)

    def test_get_service_list(self):
        response = self.client.get('/api/services/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class ServiceCreateDeleteTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.category = ServiceCategory.objects.create(name='Test1')
        self.category2 = ServiceCategory.objects.create(name='Test2')
        self.service = Service.objects.create(
            title="Test Service",
            content="This is a test service.",
            address='Address'
        )
        self.service.categories.add(self.category)
        self.client.force_login(self.user)

    def test_create_service(self):
        """Test creating a new service"""
        url = '/api/services/create/'
        data = {
            'title': 'New Service',
            'content': 'This is a new service.',
            'categories': [self.category.id, self.category2.id],
            'address': 'Address'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Service created successfully!')

        service = Service.objects.get(title='New Service')
        self.assertEqual(service.content, 'This is a new service.')
        self.assertEqual(list(service.categories.all()), [self.category, self.category2])

    def test_create_service_unauthenticated(self):
        """Test creating a event logged out"""
        self.client.logout()
        url = '/api/services/create/'
        data = {
            'title': 'Test Service',
            'content': 'This is a test service.',
            'categories': [self.category.id],
            'address': 'Address'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.service = Service.objects.create(
            title="Test Service",
            content="This is a test service.",
        )
        self.comment = ServiceComment.objects.create(
            service=self.service,
            content="This is a test comment.",
            author=self.user
        )
        self.client.force_login(self.user)

    def test_add_comment_logged_in(self):
        response = self.client.post(f'/api/services/{self.service.id}/add_comment/', {
            'content': 'This is a test comment.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a test comment.')

    def test_add_comment_logged_out(self):
        """Test adding a comment while logged out"""
        self.client.logout()
        response = self.client.post(f'/api/services/{self.service.id}/add_comment/', {
            'content': 'This is a test comment.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reply_to_comment_with_valid_id(self):
        """Test replying to a comment with a valid parent ID"""
        url = f'/api/services/{self.service.id}/add_comment/'
        response = self.client.post(url, {
            'content': 'This is a reply.',
            'parent_id': self.comment.id,
            'author_id':self.user.id
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a reply.')
        self.assertEqual(response.data['parent'], self.comment.id)

    def test_reply_to_comment_with_invalid_id(self):
        """Test replying to a comment with an invalid parent ID"""
        url = f'/api/services/{self.service.id}/add_comment/'
        response = self.client.post(url, {
            'content': 'This is a reply.',
            'parent_id': 999,
            'author_id':self.user.id
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Parent comment not found')

    def test_delete_comment_by_author(self):
        """Test that the author can delete their own comment"""
        url = f'/api/services/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Comment deleted successfully')
        self.assertFalse(ServiceComment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_by_other_user(self):
        """Test that a non-author cannot delete someone else's comment"""
        self.client.force_login(self.other_user)  # Log in as another user
        url = f'/api/services/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Permission denied')
        self.assertTrue(ServiceComment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_unauthenticated(self):
        """Test that an unauthenticated user cannot delete a comment"""
        self.client.logout()  # Log out the user
        url = f'/api/services/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(ServiceComment.objects.filter(id=self.comment.id).exists())

    def test_delete_nonexistent_comment(self):
        """Test deleting a comment that does not exist"""
        url = '/api/services/comments/999/delete/'  # Assuming 999 is an invalid ID
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Comment not found')

class CategoryTestCase(APITestCase):
    def setUp(self):
        ServiceCategory.objects.create(name="Test1")
        ServiceCategory.objects.create(name="Test2")

    def test_list_categories(self):
        response = self.client.get('/api/services/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "Test1")

# All tests below are for the filter and query
class SearchTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        profile = Profile.objects.create(user=user)
        category1 = ServiceCategory.objects.create(name="Test")
        category2 = ServiceCategory.objects.create(name="Test1")
        category3 = ServiceCategory.objects.create(name="Test2")

        service1 = Service.objects.create(
            title="Service One",
            content="Service Details",
            address="Address"
        )
        service1.categories.add(category1, category3)

        service2 = Service.objects.create(
            title="Service Two",
            content="Service Details",
            address="Address"
        )
        service2.categories.add(category2)

    def test_filter_search_title(self):
        response = self.client.get('/api/services/search/?q=One')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Service One")

    def test_filter_search_contents(self):
        response = self.client.get('/api/services/search/?q=Details')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['content'], "Service Details")
        
    def test_filter_no_match(self):
        response = self.client.get('/api/services/search/?q=invalid')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_filter_categories(self):
        response = self.client.get('/api/services/search/?categories=Test,Test2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only Service One should be returned
        self.assertEqual(response.data[0]['title'], "Service One")

    def test_filter_categories_no_match(self):
        response = self.client.get('/api/services/search/?categories=Test1,Test2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)