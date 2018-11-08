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


class ArticleFactory(factory.DjangoModelFactory):
    class Meta:
        model = Article

    user = factory.SubFactory(UserFactory)
    title = faker.name()
    description = faker.text()
    body = faker.text()
    slug = factory.Sequence(lambda n: 'map-slug%d' % n)
    image = factory.django.ImageField(color='blue')


class TestArticles(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.article = ArticleFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' +
            self.user.token())

        self.namespace = 'article'
        self.body = {
            'title': faker.name(),
            'description': faker.text(),
            'body': faker.text(),
        }
        self.create_url = reverse(self.namespace + ':create')
        self.list_url = reverse(self.namespace + ':list')
        self.update_url = reverse(
            self.namespace + ':update',
            kwargs={
                'slug': self.article.slug})
        self.delete_url = reverse(
            self.namespace + ':delete',
            kwargs={
                'slug': self.article.slug})
        self.retrieve_url = reverse(
            self.namespace + ':detail',
            kwargs={
                'slug': self.article.slug})

    def test_create_article_api(self):
        response = self.client.post(self.create_url, self.body, format='json')
        self.assertEqual(201, response.status_code)

    def test_retrieve_article_api(self):
        response = self.client.get(self.retrieve_url)
        self.assertContains(response, self.article)

    def test_list_article_api_with_parameters(self):
        self.client.post(self.create_url, self.body, format='json')
        response = self.client.get(
            self.list_url + '?q=' + self.article.slug[0])
        self.assertContains(response, self.article)

    def test_listing_articles_api(self):
        response = self.client.get(self.list_url)
        self.assertContains(response, self.article)

    def test_update_article_api(self):
        response = self.client.post(self.create_url, self.body, format='json')
        self.update_url = reverse(
            self.namespace + ':update',
            kwargs={
                'slug': response.data.get('slug')})
        response = self.client.put(self.update_url, self.body)
        self.assertEqual(200, response.status_code)

    def test_delete_article_api(self):
        response = self.client.post(self.create_url, self.body, format='json')
        self.delete_url = reverse(
            self.namespace + ':delete',
            kwargs={
                'slug': response.data.get('slug')})

        response = self.client.delete(self.delete_url)
        self.assertEqual(204, response.status_code)
