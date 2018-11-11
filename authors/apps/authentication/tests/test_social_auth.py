from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class SocialAuthViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.namespace = 'authentication'

        self.social_url = reverse(self.namespace + ':social_auth')

        self.data_no_provider = {
            "access_token": "super-awesome-access-token"
        }

        self.data_no_token = {
            "provider": "google-oauth2"
        }

        self.data_no_secret = {
            "provider": "twitter",
            "access_token": "super-awesome-access-token"
        }

        # self.data_twitter = {
        #     "provider": "twitter",
        #     "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
        #     "access_token_secret": os.getenv("TWITTER_ACCESS_SECRET")
        # }
        #
        # self.data_facebook = {
        #     "provider": "facebook",
        #     "access_token": os.getenv("FB_ACCESS_TOKEN")
        # }
        #
        # self.data_google = {
        #     "provider": "google-oauth2",
        #     "access_token": os.getenv("GOOGLE_ACCESS_TOKEN")
        # }

    def test_social_auth(self):
        # res = self.client.post(
        #     self.social_url,
        #     self.data_twitter,
        #     format='json')
        #
        # res0 = self.client.post(
        #     self.social_url,
        #     self.data_facebook,
        #     format='json')
        #
        # res4 = self.client.post(
        #     self.social_url,
        #     self.data_google,
        #     format='json')

        res1 = self.client.post(
            self.social_url,
            self.data_no_provider,
            format='json')
        res2 = self.client.post(
            self.social_url,
            self.data_no_token,
            format='json')
        res3 = self.client.post(
            self.social_url,
            self.data_no_secret,
            format='json')

        # self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(res0.status_code, status.HTTP_201_CREATED)
        # self.assertEqual(res4.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res3.status_code, status.HTTP_400_BAD_REQUEST)
