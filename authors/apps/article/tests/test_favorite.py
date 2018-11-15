from rest_framework.reverse import reverse
from rest_framework import status

from .base_like_test import BaseLikeTest


class Favorite(BaseLikeTest):

    def favorite_article(self, slug):
        url = reverse('article:favorite', args=[slug])
        response = self.client.post(
            url, format="json", HTTP_AUTHORIZATION="Bearer " + self.token)
        return response

    def test__user_can_favorite(self):
        """test user can favorite"""
        response = self.favorite_article(self.slug)
        self.assertIn("True", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test__user_cant_unfavorite_before_favoriting(self):
        """test user cant unfavorite before favoriting"""
        url = reverse('article:favorite', args=[self.slug])
        response = self.client.delete(
            url, format="json", HTTP_AUTHORIZATION="Bearer " + self.token)
        self.assertIn(
            "You have not favorited this article yet", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test__user_can_unfavorite(self):
        """test user can unfavorite article"""
        self.favorite_article(self.slug)
        url = reverse('article:favorite', args=[self.slug])
        response = self.client.delete(
            url, format="json", HTTP_AUTHORIZATION="Bearer " + self.token)
        self.assertIn("unfavorited", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test__user_cant_favorite_more_than_once(self):
        """test user cant perfrom favoriting twice"""
        self.favorite_article(self.slug)
        response = self.favorite_article(self.slug)
        self.assertIn(
            "Article already favorited", str(response.data))

    def test__user_cant_favorite_article_not_existing(self):
        """test user can favorite"""
        response = self.favorite_article('collo-deos')
        self.assertIn("That article does not exist", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test__user_cant_favorite_article_with_no_authenticatin(self):
        """test user cant favorite with no authentication"""
        url = reverse('article:favorite', args=[self.slug])
        response = self.client.post(
            url, format="json", HTTP_AUTHORIZATION="")
        self.assertIn(
            "Authentication credentials were not provided", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test__user_cant_unfavorite_article_with_no_authenticatin(self):
        """test user cant unfavorite with no authentication"""
        url = reverse('article:favorite', args=[self.slug])
        response = self.client.post(
            url, format="json", HTTP_AUTHORIZATION="")
        self.assertIn(
            "Authentication credentials were not provided", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
