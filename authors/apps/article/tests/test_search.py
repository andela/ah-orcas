from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from authors.apps.article.models import Article
from authors.apps.authentication.models import User


class TestSearch(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.namespace = 'article'
        self.list_url = reverse(self.namespace + ':list')

        user_data = {
            "user": {
                "email": "jake@jake.jake",
                "username": "jake",
                "password": "password1",
                "bio": "I work at statefarm"
            }
        }

        resp = self.client.post(
            reverse('authentication:register'),
            user_data,
            format='json')
        self.token = resp.data['token']

        assert resp.data['token'], 1

        article0 = Article(
            user=User.objects.get(username='jake'),
            body='It takes a Jacobian',
            title='How to train your dragon',
            description='Ever wonder how?',
            tags=['train', 'dragon'],
        )
        article0.save()

        article1 = Article(
            user=User.objects.get(username='jake'),
            body='This is some body',
            title='This is the title',
            description='Ever wonder what?',
            tags=['body', 'train'],
        )
        article1.save()

    def test_search(self):
        # true
        res0 = self.client.get(self.list_url + "?author=jake")
        res1 = self.client.get(self.list_url + "?tags=train")
        res2 = self.client.get(self.list_url + "?search=Jacobian")
        res3 = self.client.get(self.list_url + "?search=Jacobian&author=jake")
        res4 = self.client.get(self.list_url + "?tags=body,train")

        # false
        res5 = self.client.get(
            self.list_url +
            "?search=different&author=jolice")
        res6 = self.client.get(self.list_url + "?tags=awesome")

        self.assertEqual(res0.data["count"], 2)
        self.assertEqual(res1.data["count"], 2)
        self.assertEqual(res2.data["count"], 1)
        self.assertEqual(res3.data["count"], 1)
        self.assertEqual(res4.data["count"], 2)
        self.assertEqual(res5.data["count"], 0)
        self.assertEqual(res6.data["count"], 0)
