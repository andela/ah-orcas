from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status


class TestUserProfile(APITestCase):
    """ setup class for profile tests"""

    def setUp(self):
        """
        Prepare test environment for each testcase
        """
        self.client = APIClient()
        self.user_details = {
            'user': {
                'username': 'user1',
                'email': 'steel@gmail.com',
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

    def register_user(self):
        """
        register a new user
        """
        response = self.client.post(
            self.signup_url,
            self.user_details,
            format='json')
        return response

    def login_user(self):
        """login user to get the token"""
        response = self.client.post(
            self.login_url, self.login_data, format='json')
        return response.data['token']

    def test_get_single_user_profile(self):
        """
        test retrieve a single user profile
        """
        self.register_user()
        token = self.login_user()
        response = self.client.get(
            reverse(
                "profile:profile",
                args=['user1']), format='json', HTTP_AUTHORIZATION=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user1', str(response.data))

    def test_get_unavailable_profile(self):
        """
        test retrieve a profile that is not found/available
        """
        self.register_user()
        token = self.login_user()
        response = self.client.get(
            reverse(
                "profile:profile",
                args=['admin123']), format='json', HTTP_AUTHORIZATION=token)
        self.assertIn('There are no profiles found', str(response.data))

    def test_get_all_profiles(self):
        """
        test retrieve all the available profiles
        """
        self.register_user()
        token = self.login_user()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(self.all_profiles)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user1', str(response.data))

    def test_update_user_profile(self):
        """test profile update"""
        self.register_user()
        token = self.login_user()
        response = self.client.put(self.update_profile,
                                   {'user': {'username': 'newdata',
                                             'bio': 'I am that guy'}},
                                   format='json',
                                   HTTP_AUTHORIZATION='Bearer ' + token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('newdata', str(response.data))

    def test_update_other_user_profile(self):
        """test profile update with wrong token"""
        self.register_user()
        response = self.client.put(self.update_profile,
                                   {'user': {'username': 'newdata',
                                             'bio': 'I am that guy'}},
                                   format='json',
                                   )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_count_profiles(self):
        """tests to see if profile count matches users on db"""
        self.register_user()
        token = self.login_user()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(self.all_profiles)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))
