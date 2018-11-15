from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from authors.apps.article.models import Article
from authors.apps.authentication.models import User


class TestTag(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.namespace = 'article'

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
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.article = Article(
            user=User.objects.get(username='jake'),
            body='It takes a Jacobian',
            title='How to train your dragon',
            description='Ever wonder how?',
        )
        self.article.save()

        self.tag_url = reverse(
            self.namespace +
            ':tag_article',
            kwargs={
                'slug': self.article.slug})

        self.data0 = {
            "article": {
                "tags": ["train", "dragon"]
            }
        }

        self.data1 = {
            "article": {
                "tags": ["train", "dragon", "another one"]
            }
        }

    def test_tag_article_success(self):
        # success, new tags
        res0 = self.client.put(self.tag_url, self.data0, format='json')
        self.assertEqual(res0.status_code, status.HTTP_200_OK)
        article = Article.objects.get(slug=self.article.slug)
        self.assertEqual(len(article.tags), 2)

        # success, duplicate tags
        res1 = self.client.put(self.tag_url, self.data1, format='json')
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        article = Article.objects.get(slug=self.article.slug)
        self.assertEqual(len(article.tags), 3)

    def test_tag_article_not_found(self):
        url = reverse(
            self.namespace +
            ':tag_article',
            kwargs={
                'slug': 'some-slug'})
        res = self.client.put(url, self.data0, format='json')

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_tag_article_forbidden(self):
        client = APIClient()
        user_data = {
            "user": {
                "email": "jake@user.com",
                "username": "notjake",
                "password": "password1",
                "bio": "I don't work at statefarm"
            }
        }

        resp = self.client.post(
            reverse('authentication:register'),
            user_data,
            format='json')
        token = resp.data['token']
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        res = client.put(self.tag_url, self.data0, format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
