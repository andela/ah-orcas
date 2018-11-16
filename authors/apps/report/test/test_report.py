from django.apps import apps
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
import factory
from faker import Factory
from django.contrib.auth import get_user_model

Article = apps.get_model('article', 'Article')
faker = Factory.create()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: 'map%d' % n)
    email = factory.Sequence(lambda n: 'example_%s@map.com' % n)
    password = factory.PostGenerationMethodCall('set_password', '1234abcd')


class TestArticles(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' +
                               self.user.token())

        self.namespace = 'report'
        self.body = {
            'title': faker.text(),
            'body': faker.text(),
        }
        self.create_url = reverse(self.namespace + ':rep')

    def test_create_report_api(self):
        response = self.client.post(self.create_url, self.body, format='json')
        self.assertEqual(201, response.status_code)
