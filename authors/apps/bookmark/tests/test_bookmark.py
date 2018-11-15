from rest_framework.reverse import reverse
from rest_framework import status

from authors.apps.article.tests.base_like_test import BaseLikeTest


class Bookmark(BaseLikeTest):

    def bookmark_article(self, slug):
        url = reverse('bookmark:bookmark', args=[slug])
        response = self.client.post(
            url, format="json", HTTP_AUTHORIZATION="Bearer " + self.token)
        return response

    def test__user_can_bookmark(self):
        """test user can bookmark"""
        response = self.bookmark_article(self.slug)
        self.assertIn("True", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_bookmark_not_bookmarked(self):
        """test user cannot unbookmark before bookmarking"""
        url = reverse('bookmark:bookmark', args=[self.slug])
        response = self.client.delete(
            url, format="json", HTTP_AUTHORIZATION="Bearer " + self.token)
        self.assertIn(
            "You have not bookmarked this article yet", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test__user_can_delete_bookmark(self):
        """test user can delete bookmark"""
        self.bookmark_article(self.slug)
        url = reverse('bookmark:bookmark', args=[self.slug])
        response = self.client.delete(
            url, format="json", HTTP_AUTHORIZATION="Bearer " + self.token)
        self.assertIn("bookmark deleted", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test__user_cant_bookmark_more_than_once(self):
        """test user cant bookmark twice"""
        self.bookmark_article(self.slug)
        response = self.bookmark_article(self.slug)
        self.assertIn(
            "Article already bookmarked", str(response.data))

    def test__user_cant_bookmark_article_not_existing(self):
        """test user can bookmark"""
        response = self.bookmark_article('collo-deos')
        self.assertIn("That article does not exist", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_bookmark_article_with_no_authenticatin(self):
        """test user cant bookmark with no authentication"""
        url = reverse('bookmark:bookmark', args=[self.slug])
        response = self.client.post(
            url, format="json", HTTP_AUTHORIZATION="")
        self.assertIn(
            "Authentication credentials were not provided", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
