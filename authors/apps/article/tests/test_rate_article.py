from django.urls import reverse
import os
from ...authentication.models import User
from ..models import Article
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status


class TestRateArticle(APITestCase):
    """ class for testing email verification"""

    def setUp(self):
        """
        Prepare test environment for each testcase
        """

        self.article = {
            "title": "How to train your dragon today",
            "description": "Ever wonder how?",
            "body": "You have to believe in you",
            "image": "https://dummyimage.com/600x400/000/fff"
        }

        self.client = APIClient()
        self.article = Article()
        self.signup_url = reverse('authentication:register')
        self.user_details = {
            'user': {
                'username': 'user1',
                'email': 'evajohnson714@gmail.com',
                'password': 'somepass12345',
            }
        }
        self.user_details_2 = {
            'user': {
                'username': 'user2',
                'email': 'evajohnson715s@gmail.com',
                'password': 'somepass12345',
            }
        }
        resp = self.client.post(
            self.signup_url,
            self.user_details,
            format='json')
        res = self.client.post(
            self.signup_url,
            self.user_details_2,
            format='json')
        self.token_2 = res.data['token']
        self.token = resp.data['token']
        self.email = "test_user@gmail.com"
        self.name = "test"
        self.user = User(username=self.name, email=self.email)
        self.user.set_password("@Winners11")
        self.user.save()
        self.user_id = User.objects.get(email=self.email).pk
        self.slug = "this-is-a-question"
        title = "this is a question"
        description = "this is a description"
        body = "this is a body"
        author = self.user
        article = Article(
            user=author,
            slug=self.slug,
            body=body,
            title=title,
            description=description
        )
        article.save()
        self.rate_details = {
            "user": {
                "slug": self.slug,
                "rate": 3
            }
        }
        self.rate_url = os.environ["URL"] + \
            "api/article/" + self.slug + "/rate/"
        self.view_rates_url = os.environ["URL"] + "api/article/rate/"

        self.articles_url = os.environ["URL"] + "api/article/"
        self.create_articles_url = os.environ["URL"] + "api/article/create"

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
