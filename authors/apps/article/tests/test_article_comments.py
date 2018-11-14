from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status


class TestArticleComments(APITestCase):
    def setUp(self):
        """
        Prepare test environment for each testcase
        """
        self.client = APIClient()
        self.author_details = {
            'user': {
                'username': 'admin123',
                'email': 'admin@admin.com',
                'password': 'admin2018',
            }
        }

        self.login_data = {
            "user": {
                'email': 'admin@admin.com',
                'password': 'admin2018',
            }
        }

        self.new_comment = {
            "comments": {
                "body": "where are"
            }
        }
        self.wrong_comment = {
            "comment": {
            }
        }
        self.my_comment = {
            "comment": {
                "body": "where are fight with batman"
            }
        }
        self.new_article = {
            "title": "How to train your dragon",
            "description": "Ever wonder how?",
            "body": "You have to believe"
        }

        self.login_url = reverse('authentication:login')
        self.signup_url = reverse('authentication:register')
        self.articles_url = reverse('article:create')

        self.client.post(
            self.signup_url,
            self.author_details,
            format='json')

    def login(self):
        """login user to get the token"""
        response = self.client.post(
            self.login_url, self.login_data, format='json')
        return response.data.get('token')

    def test_add_comment(self):
        """
        test add a comment
        """
        self.token = self.login()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(
            self.articles_url,
            self.new_article,
            format='json')
        comments_url = reverse(
            'article:comment_on_an_article', kwargs={
                'slug': response.data.get('slug')})
        resp = self.client.post(comments_url, self.new_comment, format='json')
        reply_url = reverse('article:delete_comment',
                            kwargs={'slug': response.data.get('slug'),
                                    'comment_id': resp.data['id']})
        resp1 = self.client.post(reply_url,
                                 {
                                     "body": "This is a test thread?"
                                 },
                                 format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

    def test_add_comment_to_unavailable_article(self):
        """
        Test add comment to an article that does not exist
        """
        self.token = self.login()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        comments_url = reverse(
            'article:comment_on_an_article', kwargs={
                'slug': 'slug'})
        response2 = self.client.post(
            comments_url, self.new_comment, format='json')
        self.assertEqual(response2.status_code, 404)
        assert (response2.data['detail'] == "Not found.")

    def test_add_comment_without_token(self):
        """
        test add comment without authorization
        """
        self.token = self.login()
        response = self.client.post(
            self.articles_url,
            self.new_article,
            format='json')
        comments_url = reverse(
            'article:comment_on_an_article', kwargs={
                'slug': response.data.get('slug')})
        resp = self.client.post(comments_url, self.new_comment, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_comment_without_body(self):
        """
        Test post comment without comment body
        """
        self.token = self.login()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(
            self.articles_url,
            self.new_article,
            format='json')
        comments_url = reverse(
            'article:comment_on_an_article', kwargs={
                'slug': response.data.get('slug')})
        resp = self.client.post(
            comments_url,
            self.wrong_comment,
            format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_comments(self):
        """Test list all comments on an article"""
        self.token = self.login()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(
            self.articles_url,
            self.new_article,
            format='json')
        list_comments_url = reverse(
            'article:comment_on_an_article', kwargs={
                'slug': response.data.get('slug')})
        resp = self.client.get(list_comments_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_list_comments_without_token(self):
        """Test list comments without authorization"""
        self.token = self.login()
        response = self.client.post(
            self.articles_url,
            self.new_article,
            format='json')
        list_comments_url = reverse(
            'article:comment_on_an_article', kwargs={
                'slug': response.data.get('slug')})
        resp = self.client.get(list_comments_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_comments_for_invalid_article(self):
        """Test list comments for an article that does not exist"""
        self.token = self.login()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        list_comments_url = reverse(
            'article:comment_on_an_article', kwargs={
                'slug': 'slug'})
        resp = self.client.get(list_comments_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_comment(self):
        """test user should be able to update a comment for a given article"""
        self.token = self.login()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(
            self.articles_url,
            self.new_article,
            format='json')
        comments_url = reverse(
            'article:comment_on_an_article', kwargs={
                'slug': response.data.get('slug')})
        resp = self.client.post(
            comments_url, {
                'comments': {
                    'body': 'sdfsdfs sdf sdf sdfdfsdf'}}, format='json')
        url = reverse(
            'article:delete_comment',
            kwargs={
                'slug': response.data.get('slug'),
                'comment_id': resp.data['id']})
        response1 = self.client.put(
            url, {'body': 'sdfsdfs sdf sdf sdfdfsdf'}, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

    def test_delete_comments(self):
        """test user should be able to delete a comment for a given article"""
        self.token = self.login()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(
            self.articles_url,
            self.new_article,
            format='json')
        comments_url = reverse(
            'article:comment_on_an_article', kwargs={
                'slug': response.data.get('slug')})
        resp = self.client.post(comments_url, self.new_comment, format='json')
        url = reverse(
            'article:delete_comment',
            kwargs={
                'slug': response.data.get('slug'),
                'comment_id': resp.data['id']})
        response1 = self.client.delete(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

    def test_delete_unavailable_comment(self):
        """Test deleting a comment that does not exist"""
        self.token = self.login()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(
            self.articles_url,
            self.new_article,
            format='json')
        comments_url = reverse(
            'article:comment_on_an_article', kwargs={
                'slug': response.data.get('slug')})
        resp = self.client.post(comments_url, self.new_comment, format='json')
        url = reverse(
            'article:delete_comment',
            kwargs={
                'slug': resp.data.get('slug'),
                'comment_id': 1223})
        response1 = self.client.delete(url)
        self.assertEqual(response1.status_code, status.HTTP_404_NOT_FOUND)
