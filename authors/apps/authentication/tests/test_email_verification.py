from django.urls import reverse
from django.core import mail
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status


class TestEmailVerify(APITestCase):
    """ class for testing email verification"""

    def setUp(self):
        """
        Prepare test environment for each testcase
        """
        self.client = APIClient()
        self.signup_url = reverse('authentication:register')
        self.user_details = {
            'user': {
                'username': 'user1',
                'email': 'evajohnson714@gmail.com',
                'password': 'somepass12345',
            }
        }
        self.wrong_details = {
            'emai': 'levajohnson714@gmail.com',
            'password': 'somepass12345',
        }

    def test_account_verification(self):
        """
        Test whether account was verified in success.
        """
        res = self.client.post(
            self.signup_url,
            self.user_details,
            format='json')
        token = res.data['token']
        response = self.client.get(
            reverse(
                "authentication:verify",
                args=[token]))

        self.assertIn(
            'You have succesfully verified your account', str(
                response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_account_verification_with_wrong_token(self):
        """
        Test whether account can be verified with inavlid token.
        """
        self.client.post(self.signup_url, self.user_details, format='json')
        response = self.client.get(
            reverse(
                "authentication:verify",
                args=['aidhugjhxdvhjv']))
        self.assertIn('Link provided is not valid', str(response.data))
        self.assertIn('Link provided is not valid', str(response.data))

    def test_verification_mail_sent(self):
        """
        test if actual emails are being sent
        """

        self.client.post(self.signup_url, self.user_details, format='json')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Verify your account.", mail.outbox[0].body)

    def test_verification_with_bad_request(self):
        """
        test wether verification is sent when some fields are not provided
        """

        response = self.client.post(
            self.signup_url,
            self.wrong_details,
            format='json')
        self.assertTrue(response.status_code == status.HTTP_400_BAD_REQUEST)
