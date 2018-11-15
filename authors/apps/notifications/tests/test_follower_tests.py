from .base import TestNotificationsBase
from rest_framework import status
from django.urls import reverse


class TestFollowerNotifications(TestNotificationsBase):
    """
    test for followers notifications
    """

    def test_get_notifications_with_no_credential(self):
        """
        Followers notifications without token should fail
        """
        response = self.client.get(self.get_notifications)

        self.assertIn(
            "Authentication credentials were not provided", str(response.data)
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_get_notification(self):
        """
        get user notifications
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.get_notifications)
        self.assertIn(
            "notifications", str(response.data)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_notification_not_found(self):
        """
        get user notifications
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_2)
        response = self.client.get(self.get_notifications)
        self.assertIn(
            "notifications", str(response.data)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_article_notification(self):
        token = self.client.post(
            self.login_url, self.follow_me, format='json')
        url = reverse('article:favorite', args=["this-is-a-tiltle"])
        self.client.post(
            url, format="json", HTTP_AUTHORIZATION="Bearer " + self.token)
        response = self.client.get(
            self.get_notifications,
            HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_as_read_not_found(self):
        """
        get user notifications
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.put(self.edit_notifications)
        self.assertIn(
            "No notification found", str(response.data)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_mark_as_read(self):
        """
        get user notifications
        """
        data={}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.client.put(self.edit_notifications, data=data, format="json")
        response = self.client.get(self.get_notifications)
        self.assertIn(
            "notifications", str(response.data)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
