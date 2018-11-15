from .base import TestNotificationsBase
from ...article import send_notifiactions

class TestSendEmail(TestNotificationsBase):
    """
    Test that email is send to the user
    """

    def test_send_notification(self):
        slug = "this-is-a-tiltle"
        data={"body":"hello you guy"}
        response = send_notifiactions.send_article_notification(slug, data)
        self.assertEqual(True, response)

    def test_send_notification(self):
        slug = "this-is-a-title"
        data={"body":"hello you guy"}
        response = send_notifiactions.send_article_notification(slug, data)
        self.assertEqual(False, response)
