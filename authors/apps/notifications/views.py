from rest_framework.permissions import IsAuthenticated
from .models import (
    NotificationsArticle,
    NotificationsFollower)
from ..authentication.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


class Notification(APIView):
    """
    this is the endpoint class
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        return all unread notification of a users
        """
        notifications = {}
        try:
            user_profile = User.objects.get(pk=request.user.id)
            article_notifications = NotificationsArticle.objects.filter(
                subscriber_id=user_profile.pk)
            follower_notifications = NotificationsFollower.objects.filter(
                followee_id=user_profile.pk)
            for article_nortification in article_notifications:
                # create notification message from article
                # append them to notification message
                article_container = {}
                message = article_nortification.article.user.username + \
                    " commented article " + article_nortification.article.title
                article_container["message"] = message
                article_container["pk"] = article_nortification.pk,
                article_container["notification"] = "not_follower",
                article_container["is_read"] = article_nortification.is_read
                notifications["article_notifications"] = article_container

            for follower_notification in follower_notifications:
                # create notification message from follower
                # append them to notification message
                follower_container = {}
                message = follower_notification.article.user.username + \
                    " published article " + follower_notification.article.title
                follower_container["message"] = message
                follower_container["pk"] = follower_notification.pk
                follower_container["notification"] = "follower"
                follower_container["is_read"] = follower_notification.is_read
                notifications["follower_notifications"] = follower_container
            return Response({"notifications": notifications},
                            status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"response": ["Notifications not found", str(
                error)]}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, **kwargs):
        """
        update notification to read
        """
        notification = None
        try:
            pk = kwargs.get("pk")
            if kwargs.get("follower") == "follower":
                notification = NotificationsFollower.objects.get(pk=pk)
                notification.is_read = True
                notification.save()
                return Response({"response": "Notification successfully read"},
                                status=status.HTTP_200_OK)
            notification = NotificationsArticle.objects.get(pk=pk)
            notification.is_read = True
            notification.save()
            return Response({"response": "Notification successfully read"},
                            status=status.HTTP_200_OK)
        except Exception:
            return Response({"response": "No notification found"},
                            status=status.HTTP_204_NO_CONTENT)
