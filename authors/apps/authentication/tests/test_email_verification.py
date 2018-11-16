from django.urls import reverse
from django.core import mail
import jwt
from ..models import User
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status
from ....settings import SECRET_KEY
from django.contrib.auth.tokens import default_token_generator


class TestEmailVerify(APITestCase):
    """ class for testing email verification"""

    def setUp(self):
        """
        Prepare test environment for each testcase
        """
        self.client = APIClient()
        self.signup_url = reverse('authentication:register')
        self.forget_url = reverse('authentication:forget')
        self.reset_url = 'http://localhost:8000/api/users/reset'
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

        self.unsaved_email = {
            # for testiong not found password reset token
            'user': {
                'email': 'somepafdfh845@dfndj.nfn',
            }

        }
        self.password_reset = {
            "user": {
                "email": "gfgn@gn.jgkj",
                "password": "@34565jjjj"
            }
        }
        self.user_email_with_error = {
            'user': {
                'password': 'somepafdfh845',
            }
        }
        self.user_email = {
            'user': {
                'email': 'test_user@gmail.com',
            }
        }
        self.email = "test_user@gmail.com"
        self.name = "test"
        self.user = User(username=self.name, email=self.email)
        self.user.set_password("@Winners11")
        self.user.save()

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

    def test_email_send_link_verification_with_error_email(self):
        """
        Test wether response code will be 400
        if request don't have email field
        """
        response = self.client.post(
            self.forget_url,
            self.user_email_with_error,
            format='json')

        self.assertIn(
            'This field is required', str(
                response.data))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_send_link_verification_user_not_found(self):
        """
        Test wether response code will be 400
        if user not found
        """
        response = self.client.post(
            self.forget_url,
            self.unsaved_email,
            format='json')

        self.assertIn(
            "A user with this email was not found.", str(
                response.data))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_send_link_verification(self):
        """
        Test wether response code will be 200
        if request has is valid
        """
        response = self.client.post(
            self.forget_url,
            self.user_email,
            format='json'
        )
        self.assertIn(
            "Confirm your email to continue", str(
                response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_with_invalid_format(self):
        """
        test wether the response will be 400
        if the request has invalid format
        """
        user = User.objects.get(email=self.email)
        token = default_token_generator.make_token(user)
        hashed_email = jwt.encode(
            {"email": self.email}, SECRET_KEY, algorithm='HS256')
        url = self.reset_url + \
            "/" + hashed_email.decode("UTF-8") + "/" + token
        response = self.client.put(url, self.password_reset, format='json')
        self.assertIn(
            "password successfully changed", str(
                response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_with_invalid_token(self):
        """
        test wether the response will be 400
        if the request has invalid format
        """
        user = User.objects.get(email=self.email)
        token = default_token_generator.make_token(user)
        hashed_email = jwt.encode(
            {"email": self.email}, SECRET_KEY, algorithm='HS256')
        url = self.reset_url + \
            "/" + hashed_email.decode("UTF-8") + "/" + token
        resp = self.client.put(url, self.password_reset, format='json')
        response = self.client.put(url, self.password_reset, format='json')
        self.assertIn(
            "Token expired", str(
                response.data))
        self.assertIn(
            "password successfully changed", str(
                resp.data))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_reset_get(self):
        """
        test wether the response will be 400
        if the request has invalid format
        """
        user = User.objects.get(email=self.email)
        token = default_token_generator.make_token(user)
        hashed_email = jwt.encode(
            {"email": self.email}, SECRET_KEY, algorithm='HS256')
        url = self.reset_url + \
            "/" + hashed_email.decode("UTF-8") + "/" + token
        response = self.client.get(url, self.password_reset, format='json')
        self.assertIn(
            "email confirmed successfully", str(
                response.data))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        def test_password_reset_with_user_not_found(self):
            """
            test wether the response will be 400
            if the request has invalid format
            """
            user = User.objects.get(email=self.email)
            token = default_token_generator.make_token(user)
            hashed_email = jwt.encode(
                {"user": "hjhfhjd@nfjd.nnvb"}, SECRET_KEY, algorithm='HS256')
            url = self.reset_url + \
                "/" + hashed_email.decode("UTF-8") + "/" + token
            response = self.client.put(url, self.password_reset, format='json')

            self.assertIn(
                "Invalid reset tokens", str(
                    response.data))
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED)
