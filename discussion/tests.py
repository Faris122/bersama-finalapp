from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import *

class DiscussionListTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = DiscussionCategory.objects.create(name='General')
        self.discussion = Discussion.objects.create(
            title="Test Discussion",
            content="This is a test discussion.",
            author=self.user
        )
        self.discussion.categories.add(self.category)

    def test_get_discussion_list(self):
        response = self.client.get('/api/discussions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class DiscussionDetailCommentAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
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

    def test_get_discussion_detail(self):
        response = self.client.get(f'/api/discussions/{self.discussion.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Discussion")

    def test_get_discussion_detail_invalid(self):
        response = self.client.get(f'/api/discussions/874/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_comment_logged_in(self):
        response = self.client.post(f'/api/discussions/{self.discussion.id}/add_comment/', {
            'content': 'This is a test comment.'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a test comment.')

    def test_add_comment_logged_out(self):
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

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['content'], 'This is a reply.')
        self.assertEqual(response.data['parent'], self.comment.id)

    def test_reply_to_comment_with_invalid_id(self):
        """Test replying to a comment with an invalid parent ID."""
        url = f'/api/discussions/{self.discussion.id}/add_comment/'
        response = self.client.post(url, {
            'content': 'This is a reply.',
            'parent_id': 999,  # Non-existent comment ID
        }, format='json')

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Parent comment not found')