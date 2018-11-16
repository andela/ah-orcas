from .base_like_test import BaseLikeTest
import os
from rest_framework import status


class TestRateArticle(BaseLikeTest):
    """ class for testing email verification"""


    def test_rate_article_without_token(self):
        """
        test whether rate article without token will fail.
        """
        response = self.client.post(
            self.rate_url,
            self.rate_details,
            format='json')
        self.assertIn(
            'Authentication credentials were not provided.', str(
                response.data))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rate_article(self):
        """
        test rate article.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(
            self.rate_url,
            self.rate_details,
            format='json')
        self.assertIn(
            'sucessfully rated', str(
                response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_rate_article_not_found(self):
        """
        test whether rate article without article will fail.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.rate_details["user"]["slug"] = "-ss-dd-dd-ff"
        response = self.client.post(
            self.rate_url,
            self.rate_details,
            format='json')
        self.assertIn(
            'Article not found', str(
                response.data))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_rate_article_invalid_rate(self):
        """
        test whether rate article with invalid data will fail.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.rate_details["user"]["rate"] = 7
        response = self.client.post(
            self.rate_url,
            self.rate_details,
            format='json')
        self.rate_details["user"]["rate"] = 0
        resp = self.client.post(
            self.rate_url,
            self.rate_details,
            format='json')
        self.assertIn(
            'invalid rate value should be > 0 or <=5', str(
                response.data))
        self.assertIn(
            'invalid rate value should be > 0 or <=5', str(
                resp.data))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_rate_article(self):
        """
        test whether rate article with token.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.client.post(
            self.rate_url,
            self.rate_details,
            format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_2)
        self.rate_details["user"]['rate'] = 4
        self.client.post(
            self.rate_url,
            self.rate_details,
            format='json')
        response = self.client.get(
            self.view_rates_url + str(1) + "/",
            format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_rate_article_not_found(self):
        """
        test whether get rates.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(
            self.view_rates_url + str(2) + "/",
            format='json')
        self.assertEqual(
            0,
            response.data["rates"])
        self.assertEqual(204, status.HTTP_204_NO_CONTENT)
