import json
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
    image = faker.url()


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
        text = "Will it rain, Will it rain today, " \
            "Will it rain today Will it rain today " \
            "Will it rain today Will it rain today, " \
            "Will it rain today Will it rain today " \
            "Will it rain today Will it rain today " \
            "Will it rain today Will it rain today," \
            "Will it rain today Will it rain today Will it rain "
        self.body = {
            'title': faker.name(),
            'description': faker.text(),
            'body': faker.text(),
        }
        self.article_body = {
            "title": "Test reading time 300 ",
            "description": "Is a new day again?",
            "body": text
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
        response1 = self.client.post(
            self.create_url,
            self.article_body,
            format='json')
        self.assertEqual(201, response.status_code)
        self.assertIn('2mins', str(response1.data))

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

    def create_many_articles(self):
        for i in range(1, 15):
            ''' next line will make the tilte unique and ensures its posted'''
            self.body['title'] = self.body['title'] + str(i)
            self.client.post(self.create_url, self.body, format='json')

    def test_articles_are_paginated(self):
        self.create_many_articles()
        response = self.client.get(self.list_url)
        '''See if  the return of get articles has count, next and previous
           articles'''
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("count", response.data)

    def test_more_than_ten_articles_are_paginated(self):
        self.create_many_articles()
        response = self.client.get(self.list_url)
        self.assertEqual('http://testserver/api/article/?page=2',
                         response.data["next"])
        self.assertEqual(response.data["previous"], None)
        self.assertEqual(response.data["count"], 15)

    def test_number_of_articles_in_page(self):
        """This one tests that a given page returns tens articles"""
        self.create_many_articles()
        response = self.client.get(self.list_url)
        assert len(response.data["results"]) == 10

    def test_if_article_returns_facebook_url(self):
        """This method tests whether the API returns facebook url"""
        response = self.client.get(self.list_url)
        self.assertIn("facebook", json.dumps(response.data))

    def test_if_article_returns_linkedin_url(self):
        """This method tests whether the API returns linkedin url"""
        response = self.client.get(self.list_url)
        self.assertIn("Linkedin", json.dumps(response.data))

    def test_if_article_returns_twitter_url(self):
        """This method tests whether the API returns twitter url"""
        response = self.client.get(self.list_url)
        self.assertIn("twitter", json.dumps(response.data))

    def test_if_article_returns_mail_url(self):
        """This method tests whether the API returns mail url"""
        response = self.client.get(self.list_url)
        self.assertIn("mail", json.dumps(response.data))

    def test_article_returns_url(self):
        """This method tests whether the API returns url"""
        response = self.client.get(self.list_url)
        self.assertIn("url", json.dumps(response.data))
