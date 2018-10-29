from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


class UserTest(TestCase):
    """"""

    def setUp(self):
        self.client = APIClient()
        self.namespace = 'authentication'

        # valid data
        self.data = {
            "user": {
                "email": "j@k.in",
                "password": "abaoihs4",
                "username": "j"}}

        # no password
        self.no_password = {"user": {"username": "ja", "email": "j@k.com"}}

        # no username
        self.no_username = {
            "user": {
                "email": "j@k.com",
                "password": "abadoihs4"}}

        # no email
        self.no_email = {"user": {"username": "jake", "password": "abadoihs4"}}

        # invalid email
        self.invalid_email = {
            "user": {
                "email": "j@",
                "password": "abaoihs4",
                "username": "j"}}

        # invalid username
        self.invalid_username = {
            "user": {
                "email": "j@k.in",
                "password": "abaoihs4",
                "username": "@$"}}

    def test_user_registration(self):
        url = reverse(self.namespace + ':register')

        res = self.client.post(url, self.data, format='json')
        token = res.data["token"]
        self.assertIsNotNone(token)
        self.assertEqual(201, res.status_code)

        # empty password
        res1 = self.client.post(url, self.no_password, format='json')
        res2 = self.client.post(url, self.no_username, format='json')
        res3 = self.client.post(url, self.no_email, format='json')
        res4 = self.client.post(url, self.invalid_email, format='json')
        res5 = self.client.post(url, self.invalid_username, format='json')

        self.assertEqual(400, res1.status_code)
        self.assertEqual(400, res2.status_code)
        self.assertEqual(400, res3.status_code)
        self.assertEqual(400, res4.status_code)
        self.assertEqual(400, res5.status_code)
