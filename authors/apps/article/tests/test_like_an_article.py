from .base_like_test import BaseLikeTest
import os
from rest_framework import status


class TestLikeArticle(BaseLikeTest):
    """Test like article class"""

    def test_like_article_without_token(self):
        """
        Test whether like request without token will fail
        """
        response = self.client.post(self.like_url, self.data, format='json')
        self.assertIn(
            "Authentication credentials were not provided", str(
                response.data))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_like_article_of_article_not_found(self):
        """test whether like request with
        an article slug that doesn't exist will fail"""
        slug = "s-sss-ss-s"
        self.like_url = os.environ["URL"] + \
            "api/article/" + "like/" + slug + "/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.like_url, self.data, format='json')
        self.assertIn("No article found", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_like_article(self):
        """
        test whether like request with
        an article slug that doesn't exist will fail
        """

        self.like_url = os.environ["URL"] + \
            "api/article/" + "like/" + self.slug + "/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.like_url, self.data, format='json')
        self.assertIn("article successfully liked", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_like_twice_article(self):
        """
        test whether like request to an
        already liked article will unlike it
        """

        self.like_url = os.environ["URL"] + \
            "api/article/" + "like/" + self.slug + "/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.client.post(self.like_url, self.data, format='json')
        response = self.client.post(self.like_url, self.data, format='json')
        self.assertIn("article successfully unliked", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_likes_article_with_no_likes(self):
        """
        test whether quality
        """

        self.like_url = os.environ["URL"] + \
            "api/article/" + "like/" + self.slug + "/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.like_url, format='json')
        self.assertIn("0", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_likes_article(self):
        """
        test get likes of an article
        """

        self.like_url = os.environ["URL"] + \
            "api/article/" + "like/" + self.slug + "/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.like_url, self.data, format='json')
        response = self.client.get(self.like_url, format='json')
        self.assertIn("1", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_like_article_of_article_not_found(self):
        """
        test like article with a non-existing slug
        """
        slug = "s-sss-ss-s"
        self.like_url = os.environ["URL"] + \
            "api/article/" + "like/" + slug + "/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.like_url, format='json')
        self.assertIn("No article found", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
