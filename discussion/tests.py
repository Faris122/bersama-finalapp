from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import *

class ListTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = DiscussionCategory.objects.create(name='General')
        self.category2 = DiscussionCategory.objects.create(name='Help')
        self.discussion = Discussion.objects.create(
            title="Test Discussion",
            content="This is a test discussion.",
            author=self.user
        )
        self.discussion.categories.add(self.category)
        self.client.force_login(self.user)

    def test_get_discussion_list(self):
        response = self.client.get('/api/discussions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class CreateDeleteTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.category = DiscussionCategory.objects.create(name='General')
        self.category2 = DiscussionCategory.objects.create(name='Help')
        self.discussion = Discussion.objects.create(
            title="Test Discussion",
            content="This is a test discussion.",
            author=self.user
        )
        self.discussion.categories.add(self.category)
        self.client.force_login(self.user)

    def test_create_discussion(self):
        """Test creating a new discussion."""
        url = '/api/discussions/create/'
        data = {
            'title': 'New Discussion',
            'content': 'This is a new discussion.',
            'categories': [self.category.id, self.category2.id]  # Use category IDs
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Discussion created successfully!')

        discussion = Discussion.objects.get(title='New Discussion')
        self.assertEqual(discussion.content, 'This is a new discussion.')
        self.assertEqual(discussion.author.username, 'testuser')
        self.assertEqual(list(discussion.categories.all()), [self.category, self.category2])

    def test_create_discussion_unauthenticated(self):
        """Test creating a discussion without authentication."""
        self.client.logout()
        url = '/api/discussions/create/'
        data = {
            'title': 'Test Discussion',
            'content': 'This is a test discussion.',
            'categories': [self.category.id]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_discussion_by_author(self):
        """Test that the author can delete their own discussion."""
        url = f'/api/discussions/{self.discussion.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Discussion deleted successfully')
        self.assertFalse(Discussion.objects.filter(id=self.discussion.id).exists())

    def test_delete_discussion_by_other_user(self):
        """Test that a non-author cannot delete someone else's discussion."""
        self.client.force_login(self.other_user)  # Log in as another user
        url = f'/api/discussions/{self.discussion.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Permission denied')
        self.assertTrue(Discussion.objects.filter(id=self.discussion.id).exists())

    def test_delete_discussion_unauthenticated(self):
        """Test that an unauthenticated user cannot delete a discussion."""
        self.client.logout()  # Log out the user
        url = f'/api/discussions/{self.discussion.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Discussion.objects.filter(id=self.discussion.id).exists())

    def test_delete_nonexistent_discussion(self):
        """Test deleting a discussion that does not exist."""
        url = '/api/discussions/999/delete/'  # Assuming 999 is an invalid ID
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Discussion not found')


class CommentTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.discussion = Discussion.objects.create(
            title="Test Discussion",
            content="This is a test discussion.",
            author=self.user
        )
        self.comment = DiscussionComment.objects.create(
            post=self.discussion,
            content="This is a test comment.",
            author=self.user
        )
        self.client.force_login(self.user)

    def test_add_comment_logged_in(self):
        """Test if the user can add a comment."""
        response = self.client.post(f'/api/discussions/{self.discussion.id}/add_comment/', {
            'content': 'This is a test comment.'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a test comment.')

    def test_add_comment_logged_out(self):
        """Test if comments cannot be added if the user is logged out."""
        self.client.logout()
        response = self.client.post(f'/api/discussions/{self.discussion.id}/add_comment/', {
            'content': 'This is a test comment.'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reply_to_comment_with_valid_id(self):
        """Test replying to a comment with a valid parent ID."""
        url = f'/api/discussions/{self.discussion.id}/add_comment/'
        response = self.client.post(url, {
            'content': 'This is a reply.',
            'parent_id': self.comment.id,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a reply.')
        self.assertEqual(response.data['parent'], self.comment.id)

    def test_reply_to_comment_with_invalid_id(self):
        """Test replying to a comment with an invalid parent ID."""
        url = f'/api/discussions/{self.discussion.id}/add_comment/'
        response = self.client.post(url, {
            'content': 'This is a reply.',
            'parent_id': 999,  # Non-existent comment ID
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Parent comment not found')

    def test_delete_comment_by_author(self):
        """Test that the author can delete their own comment."""
        url = f'/api/discussions/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Comment deleted successfully')
        self.assertFalse(DiscussionComment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_by_other_user(self):
        """Test that a non-author cannot delete someone else's comment."""
        self.client.force_login(self.other_user)  # Log in as another user
        url = f'/api/discussions/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Permission denied')
        self.assertTrue(DiscussionComment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_unauthenticated(self):
        """Test that an unauthenticated user cannot delete a comment."""
        self.client.logout()  # Log out the user
        url = f'/api/discussions/comments/{self.comment.id}/delete/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(DiscussionComment.objects.filter(id=self.comment.id).exists())

    def test_delete_nonexistent_comment(self):
        """Test deleting a comment that does not exist."""
        url = '/api/discussions/comments/999/delete/'  # Assuming 999 is an invalid ID
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Comment not found')

class CategoryTestCase(APITestCase):
    def setUp(self):
        DiscussionCategory.objects.create(name="General")
        DiscussionCategory.objects.create(name="Specific")

    def test_list_categories(self):
        """Test the listing of categories."""
        response = self.client.get('/api/discussions/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "General")

class SearchTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username="testuser", password="testpass")
        category1 = DiscussionCategory.objects.create(name="General")
        category2 = DiscussionCategory.objects.create(name="Specific")
        category3 = DiscussionCategory.objects.create(name="Help")

        discussion1 = Discussion.objects.create(
            title="Discussion One",
            content="Discussion Details",
            author=user
        )
        discussion1.categories.add(category1, category3)

        discussion2 = Discussion.objects.create(
            title="Discussion Two",
            content="Discussion Details",
            author=user
        )
        discussion2.categories.add(category2)

    def test_filter_search_title(self):
        """Test if query search works on title."""
        response = self.client.get('/api/discussions/search/?q=One')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Discussion One")

    def test_filter_search_contents(self):
        """Test if query search works on content."""
        response = self.client.get('/api/discussions/search/?q=Details')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['content'], "Discussion Details")
        
    def test_filter_no_match(self):
        """Test invalid search."""
        response = self.client.get('/api/discussions/search/?q=invalid')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_filter_categories(self):
        """Test if discussions can be filtered by category."""
        response = self.client.get('/api/discussions/search/?categories=General,Help')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only Discussion One should be returned
        self.assertEqual(response.data[0]['title'], "Discussion One")

    def test_filter_categories_no_match(self):
        """Test if discussions can be filtered by category (no match)."""
        response = self.client.get('/api/discussions/search/?categories=Specific,Help')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)