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

        # password not alphanumeric
        self.non_alpha_numeric_password = {
            "user": {
                "email": "jake@jake.com",
                "password": "password",
                "username": "jake"
            }
        }

        # email already exists
        self.email_exists = {
            "user": {
                "email": "j@k.in",
                "password": "abaoihs4",
                "username": "notjake"}}

        # password less than 8 characters long
        self.short_password = {
            "user": {
                "email": "john@k.in",
                "password": "not90",
                "username": "notno"}}

    def test_user_registration(self):
        url = reverse(self.namespace + ':register')

        res = self.client.post(url, self.data, format='json')
        token = res.data["token"]
        self.assertIsNotNone(token)
        self.assertEqual(201, res.status_code)

        res1 = self.client.post(url, self.no_password, format='json')
        res2 = self.client.post(url, self.no_username, format='json')
        res3 = self.client.post(url, self.no_email, format='json')
        res4 = self.client.post(url, self.invalid_email, format='json')
        res5 = self.client.post(url, self.invalid_username, format='json')
        res6 = self.client.post(
            url, self.non_alpha_numeric_password, format='json')
        res7 = self.client.post(url, self.email_exists, format='json')
        res8 = self.client.post(url, self.short_password, format='json')

        self.assertEqual(400, res1.status_code)
        self.assertEqual(400, res2.status_code)
        self.assertEqual(400, res3.status_code)
        self.assertEqual(400, res4.status_code)
        self.assertEqual(400, res5.status_code)
        self.assertEqual(400, res6.status_code)
        self.assertEqual(400, res7.status_code)
        self.assertEqual(400, res8.status_code)

        self.assertEqual(
            res1.data["errors"]["password"][0],
            "This field is required.")
        self.assertEqual(
            res2.data["errors"]["username"][0],
            "This field is required.")
        self.assertEqual(
            res3.data["errors"]["email"][0],
            "This field is required.")
        self.assertEqual(
            res4.data["errors"]["email"][0],
            "Enter a valid email address.")
        self.assertEqual(
            res5.data["errors"]["username"][0],
            "Username should only contain alphanumeric characters")
        self.assertEqual(
            res6.data["errors"]["password"][0],
            "Password must contain at least one digit")
        self.assertEqual(
            res7.data["errors"]["email"][0],
            "user with this email already exists.")
        self.assertEqual(
            res8.data["errors"]["password"][0],
            "Ensure this field has at least 8 characters.")
