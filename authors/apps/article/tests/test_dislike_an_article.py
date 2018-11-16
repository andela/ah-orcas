from .base_like_test import BaseLikeTest
import os
from rest_framework import status


class TestDislikeArticle(BaseLikeTest):
    """Test dislike article class"""

    def test_dislike_article_without_token(self):
        """
        Test whether dislike request without token will fail
        """
        response = self.client.post(self.dislike_url, self.data, format='json')
        self.assertIn(
            "Authentication credentials were not provided", str(
                response.data))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dislike_article_of_article_not_found(self):
        """
        test whether dislike request with
         an article slug that doesn't exist will fail
        """
        slug = "s-sss-ss-s"
        self.dislike_url = os.environ["URL"] + \
            "api/article/" + "dislike/" + slug + "/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.dislike_url, self.data, format='json')
        self.assertIn("No article found", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_dislike_article(self):
        """
        test dislike article
        """

        self.dislike_url = os.environ["URL"] + \
            "api/article/" + "dislike/" + self.slug + "/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.dislike_url, self.data, format='json')
        self.assertIn("article successfully disliked", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_dislike_article_with_no_likes(self):
        """
        test dislike article
        """

        self.dislike_url = os.environ["URL"] + \
            "api/article/" + "dislike/" + self.slug + "/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.dislike_url, self.data, format='json')
        self.assertIn("0", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dislike_twice_article(self):
        """
        test whether like request to an
        already disliked article will undisliked it
        """

        self.dislike_url = os.environ["URL"] + \
            "api/article/" + "dislike/" + self.slug + "/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.client.post(self.dislike_url, self.data, format='json')
        response = self.client.post(self.dislike_url, self.data, format='json')
        self.assertIn("article successfully undisliked", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_dislikes_article(self):
        """
        test get article dislikes
        """

        self.dislike_url = os.environ["URL"] + \
            "api/article/" + "dislike/" + self.slug + "/"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.dislike_url, self.data, format='json')
        response = self.client.get(self.dislike_url, format='json')
        self.assertIn("1", str(response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
