from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import *
from account.models import Profile
from django.utils.timezone import now, timedelta

class EventListTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile = Profile.objects.create(user=self.user)
        self.category = EventCategory.objects.create(name='Test1')
        self.category2 = EventCategory.objects.create(name='Test2')
        self.event = Event.objects.create(
            title="Test Event",
            content="This is a test event.",
            address="Address",
            datetime_start=(now() + timedelta(days=1)).isoformat(),
            datetime_end=(now() + timedelta(days=2)).isoformat(),
        )
        self.event.categories.add(self.category)
        self.client.force_login(self.user)

    def test_get_event_list(self):
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class EventCreateDeleteTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.category = EventCategory.objects.create(name='Test1')
        self.category2 = EventCategory.objects.create(name='Test2')
        self.event = Event.objects.create(
            title="Test Event",
            content="This is a test event.",
            address='Address',
            datetime_start=(now() + timedelta(days=1)).isoformat(),
            datetime_end=(now() + timedelta(days=2)).isoformat(),
        )
        self.event.categories.add(self.category)
        self.client.force_login(self.user)

    def test_create_event(self):
        """Test creating a new event"""
        url = '/api/events/create/'
        data = {
            'title': 'New Event',
            'content': 'This is a new event.',
            'categories': [self.category.id, self.category2.id],
            'address': 'Address',
            "datetime_start": (now() + timedelta(days=1)).isoformat(),
            "datetime_end": (now() + timedelta(days=2)).isoformat()
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Event created successfully!')

        event = Event.objects.get(title='New Event')
        self.assertEqual(event.content, 'This is a new event.')
        self.assertEqual(list(event.categories.all()), [self.category, self.category2])

    def test_create_event_unauthenticated(self):
        """Test creating a event logged out"""
        self.client.logout()
        url = '/api/events/create/'
        data = {
            'title': 'Test Event',
            'content': 'This is a test event.',
            'categories': [self.category.id],
            'address': 'Address',
            "datetime_start": (now() + timedelta(days=1)).isoformat(),
            "datetime_end": (now() + timedelta(days=2)).isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_event_end_before_start(self):
        """Test creating a new event, with end before start datetime"""
        url = '/api/events/create/'
        data = {
            'title': 'New Event',
            'content': 'This is a new event.',
            'categories': [self.category.id, self.category2.id],
            'address': 'Address',
            "datetime_start": (now() + timedelta(days=2)).isoformat(),
            "datetime_end": (now() + timedelta(days=1)).isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("End time must be after the start time.", response.data["datetime_end"])


class CommentTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.event = Event.objects.create(
            title="Test Event",
            content="This is a test event.",
            address="Address",
            datetime_start=(now() + timedelta(days=1)).isoformat(),
            datetime_end=(now() + timedelta(days=2)).isoformat()
        )
        self.comment = EventComment.objects.create(
            event=self.event,
            content="This is a test comment.",
            author=self.user
        )
        self.client.force_login(self.user)

    def test_add_comment_logged_in(self):
        response = self.client.post(f'/api/events/{self.event.id}/add_comment/', {
            'content': 'This is a test comment.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a test comment.')

    def test_add_comment_logged_out(self):
        """Test adding a comment while logged out"""
        self.client.logout()
        response = self.client.post(f'/api/events/{self.event.id}/add_comment/', {
            'content': 'This is a test comment.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reply_to_comment_with_valid_id(self):
        """Test replying to a comment with a valid parent ID"""
        url = f'/api/events/{self.event.id}/add_comment/'
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
        url = f'/api/events/{self.event.id}/add_comment/'
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
        url = f'/api/events/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Comment deleted successfully')
        self.assertFalse(EventComment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_by_other_user(self):
        """Test that a non-author cannot delete someone else's comment"""
        self.client.force_login(self.other_user)  # Log in as another user
        url = f'/api/events/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Permission denied')
        self.assertTrue(EventComment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_unauthenticated(self):
        """Test that an unauthenticated user cannot delete a comment"""
        self.client.logout()  # Log out the user
        url = f'/api/events/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(EventComment.objects.filter(id=self.comment.id).exists())

    def test_delete_nonexistent_comment(self):
        """Test deleting a comment that does not exist"""
        url = '/api/events/comments/999/delete/'  # Assuming 999 is an invalid ID
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Comment not found')

class CategoryTestCase(APITestCase):
    def setUp(self):
        EventCategory.objects.create(name="Test1")
        EventCategory.objects.create(name="Test2")

    def test_list_categories(self):
        response = self.client.get('/api/events/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "Test1")

# All tests below are for the filter and query
class SearchTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        profile = Profile.objects.create(user=user)
        category1 = EventCategory.objects.create(name="Test")
        category2 = EventCategory.objects.create(name="Test1")
        category3 = EventCategory.objects.create(name="Test2")

        event1 = Event.objects.create(
            title="Event One",
            content="Event Details",
            address="Address",
            datetime_start=(now() + timedelta(days=1)).isoformat(),
            datetime_end=(now() + timedelta(days=2)).isoformat(),
        )
        event1.categories.add(category1, category3)

        event2 = Event.objects.create(
            title="Event Two",
            content="Event Details",
            address="Address",
            datetime_start=(now() + timedelta(days=1)).isoformat(),
            datetime_end=(now() + timedelta(days=2)).isoformat(),
        )
        event2.categories.add(category2)

    def test_filter_search_title(self):
        response = self.client.get('/api/events/search/?q=One')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Event One")

    def test_filter_search_contents(self):
        response = self.client.get('/api/events/search/?q=Details')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['content'], "Event Details")
        
    def test_filter_no_match(self):
        response = self.client.get('/api/events/search/?q=invalid')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_filter_categories(self):
        response = self.client.get('/api/events/search/?categories=Test,Test2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only Event One should be returned
        self.assertEqual(response.data[0]['title'], "Event One")

    def test_filter_categories_no_match(self):
        response = self.client.get('/api/events/search/?categories=Test1,Test2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)