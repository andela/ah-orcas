from django.urls import reverse
from ...authentication.models import User
from ...article.models import Article
import os
from rest_framework.test import APIClient
from rest_framework.test import APITestCase


class TestNotificationsBase(APITestCase):
    """ setup class for follow profile tests"""

    def setUp(self):
        """
        Prepare test environment for each testcase
        """
        self.client = APIClient()
        self.user_details = {
            'user': {
                'username': 'steel',
                'email': 'steel@gmail.com',
                'password': 'somepass12345',
            }
        }
        self.login_url = reverse('authentication:login')
        self.signup_url = reverse('authentication:register')
        self.all_profiles = reverse('profile:all_profiles')
        self.update_profile = reverse('authentication:update_profile')
        self.follow_me = {
            'user': {
                'username': 'bond',
                'email': 'bond@gmail.com',
                'password': 'somepass12345',
            }
        }

        self.login_data = {
            "user": {
                'email': 'steel@gmail.com',
                'password': 'somepass12345'
            }
        }
        self.user_details_2 = {
            'user': {
                'username': 'user2',
                'email': 'evajohnson715s@gmail.com',
                'password': 'somepass12345',
            }
        }
        self.new_comment = {
            "comments": {
                "body": "where are"
            }
        }
        res = self.client.post(
            self.signup_url,
            self.user_details_2,
            format='json')
        self.token_2 = res.data['token']
        self.comments_url = reverse(
            'article:comment_on_an_article', kwargs={
                'slug': "this-is-a-tiltle"})
        self.email = "test_user@gmail.com"
        self.name = "test"
        self.user = User(username=self.name, email=self.email)
        self.user.set_password("@Winffners11")
        self.user.save()
        self.user_2 = User(username="jjdhg gjfg",
                           email="ndnfn@jfjg.hfg")
        self.user_2.set_password("@Winffners11")
        self.user_2.save()
        self.user_id = User.objects.get(email=self.email).pk
        self.slug = "this-is-a-question"
        title = "this is a question"
        description = "this is a description"
        body = "this is a body"
        author = self.user
        article = Article(
            user=author,
            slug=self.slug,
            body=body,
            title=title,
            description=description
        )
        article.save()
        self.rate_details = {
            "user": {
                "slug": self.slug,
                "rate": 3
            }
        }
        self.data = {}
        self.rate_url = os.environ["URL"] + \
            "api/article/" + self.slug + "/rate/"
        self.view_rates_url = os.environ["URL"] + "api/article/rate/"
        self.dislike_url = os.environ["URL"] + \
            "api/article/" + "dislike/" + self.slug + "/"
        self.view_dislikes_url = os.environ["URL"] + "api/article/rate/"
        self.like_url = os.environ["URL"] + \
            "api/article/" + "like/" + self.slug + "/"
        self.view_likes_url = os.environ["URL"] + "api/article/rate/"
        self.articles_url = os.environ["URL"] + "api/article/"
        self.create_articles_url = os.environ["URL"] + "api/article/create"
        self.get_notifications = os.environ["URL"] + "api/notifications"
        self.edit_notifications = os.environ["URL"] + "api/notifications/" +\
            "4" + "/follower"
        self.edit_notifications_2 = os.environ["URL"] + "api/notifications/" +\
            "1" + "unfollower"
        self.register_user(self.user_details)
        self.register_user(self.follow_me)
        self.token = self.login_user()
        self.client.post(
            reverse(
                "profile:follow",
                args=['bond']),
            format='json',
            HTTP_AUTHORIZATION='Bearer ' +
            self.token)
        token = self.client.post(
            self.login_url, self.follow_me, format='json')
        data = {"title": "this is a tiltle"}
        self.client.post(
            self.create_articles_url,
            data=data, format='json',
            HTTP_AUTHORIZATION='Bearer ' + token.data['token'])

    def login_user(self):
        """login user to get the token"""
        response = self.client.post(
            self.login_url, self.login_data, format='json')
        return response.data['token']

    def register_user(self, user_details):
        """
        register a new user
        """
        self.client.post(
            self.signup_url,
            user_details,
            format='json')

    def favorite_article(self, slug):
        url = reverse('article:favorite', args=[slug])
        response = self.client.post(
            url, format="json", HTTP_AUTHORIZATION="Bearer " + self.token)
        return response
