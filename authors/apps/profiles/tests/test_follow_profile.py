from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status


class TestFollowUserProfile(APITestCase):
    """ setup class for follow profile tests"""

    def setUp(self):
        """
        Prepare test environment for each testcase
        """
        self.client = APIClient()
        self.user_details = {
            'user': {
                'username': 'steel',
                'email': 'steel@gmail.com',
                'password': 'somepass12345',
            }
        }
        self.follow_me = {
            'user': {
                'username': 'bond',
                'email': 'bond@gmail.com',
                'password': 'somepass12345',
            }
        }

        self.login_data = {
            "user": {
                'email': 'steel@gmail.com',
                'password': 'somepass12345'
            }
        }

        self.login_url = reverse('authentication:login')
        self.signup_url = reverse('authentication:register')
        self.all_profiles = reverse('profile:all_profiles')
        self.update_profile = reverse('authentication:update_profile')

    def register_user(self, user_details):
        """
        register a new user
        """
        self.client.post(
            self.signup_url,
            user_details,
            format='json')

    def login_user(self):
        """login user to get the token"""
        response = self.client.post(
            self.login_url, self.login_data, format='json')
        return response.data['token']

    def test_follow_another_user_profile(self):
        """
        test follow another profile
        """
        self.register_user(self.user_details)
        self.register_user(self.follow_me)
        token = self.login_user()
        response = self.client.post(
            reverse(
                "profile:follow",
                args=['bond']),
            format='json',
            HTTP_AUTHORIZATION='Bearer ' +
            token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('True', str(response.data))

    def test_un_follow_another_user_profile(self):
        """
        test un follow another profile
        """
        self.register_user(self.user_details)
        self.register_user(self.follow_me)
        token = self.login_user()
        response = self.client.delete(
            reverse(
                "profile:follow",
                args=['bond']),
            format='json', HTTP_AUTHORIZATION='Bearer ' + token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('False', str(response.data))

    def test_follow_my_self(self):
        """
        test follow myself
        """
        self.register_user(self.user_details)
        self.register_user(self.follow_me)
        token = self.login_user()
        response = self.client.post(
            reverse(
                "profile:follow",
                args=['steel']),
            format='json', HTTP_AUTHORIZATION='Bearer ' + token)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn(
            'You can only follow others, not yourself', str(response.data))

    def test_follow_without_authentication(self):
        """
        test follow another profile
        """
        self.register_user(self.user_details)
        self.register_user(self.follow_me)
        response = self.client.post(
            reverse(
                "profile:follow",
                args=['steel']),
            format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            'Authentication credentials were not provided', str(response.data))
