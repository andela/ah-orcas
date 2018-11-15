from django.urls import reverse
import os
from ...authentication.models import User
from ..models import Article
from rest_framework.test import APIClient
from rest_framework.test import APITestCase


class BaseLikeTest(APITestCase):
    """ class for testing like and dislike"""

    def setUp(self):
        """
        Prepare test environment for each testcase
        """

        self.client = APIClient()
        self.article = Article()
        self.signup_url = reverse('authentication:register')
        self.user_details = {
            'user': {
                'username': 'user1',
                'email': 'evajohnson714@gmail.com',
                'password': 'somepass12345',
            }
        }
        self.user_details_2 = {
                 'user': {
                     'username': 'user2',
                     'email': 'evajohnson715s@gmail.com',
                     'password': 'somepass12345',
                 }
             }
        resp = self.client.post(
            self.signup_url,
            self.user_details,
            format='json')
        res = self.client.post(
            self.signup_url,
            self.user_details_2,
            format='json')
        self.token_2 = res.data['token']
        self.token = resp.data['token']
        self.email = "test_user@gmail.com"
        self.name = "test"
        self.user = User(username=self.name, email=self.email)
        self.user.set_password("@Winffners11")
        self.user.save()
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
        self.edit_notifications = os.environ["URL"] + "api/notifications" +\
            "1" + "follower"
        self.edit_notifications_2 = os.environ["URL"] + "api/notifications" +\
            "1" + "unfollower"
