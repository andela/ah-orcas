from ..profiles.models import UserProfile, Follow
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .models import Article, Favorite
from authors.settings import DEFAULT_DOMAIN, EMAIL_HOST_USER
from rest_framework.generics import CreateAPIView
from .serializers import RateArticleSerializer
from .models import RateArticle
from rest_framework import status
from rest_framework.response import Response
from ..authentication.renderers import UserJSONRenderer
from rest_framework.permissions import IsAuthenticated
from ..notifications.models import NotificationsFollower, NotificationsArticle


def send_article_notification(slug, data):
    """
    send email to article favourites
    """
    try:
        article = Article.objects.get(slug=slug)
        subscribers = Favorite.objects.filter(article=article)
        for subscriber in subscribers:
            message = request.user.username + " commented on this article "
            link = DEFAULT_DOMAIN + '/api/article/detail/' + \
                article.slug
            msg = render_to_string('article_alert.html', {
                'user': subscriber.user.username,
                "link": link,
                "message": message,
                "comment": data["body"]
            })
            send_mail('Authors Heaven New Article!',
                      'New Comment!!!!',
                      EMAIL_HOST_USER,
                      [subscriber.user.email],
                      html_message=msg,
                      fail_silently=False)
            NotificationsArticle(
                subscriber_id=subscriber.pk,
                article_id=article.pk).save()
        return True
    except Exception as error:
        return False


def send_followers_notification(instance, user):
    """
    send email to user following the author
    """
    try:
        profile = UserProfile.objects.get(user=user)
        followers = Follow.objects.filter(follower=profile)
        article = Article.objects.get(title=instance["title"])
        for follower in followers:
            message = article.user.username + " published new article "
            link = DEFAULT_DOMAIN + '/api/article/detail/' + \
                article.slug
            follower_message = render_to_string('followee_alert.html', {
                'user': follower.followee.user.username,
                "link": link,
                "message": message,
                "title": instance["title"]
            })
            send_mail('Authors Heaven New Article!',
                      'New Article!!!!',
                      EMAIL_HOST_USER,
                      [follower.followee.user.email],
                      html_message=follower_message,
                      fail_silently=False)
            NotificationsFollower(
                follower=profile,
                followee=follower.followee,
                article=article).save()
            return True
    except Exception as error:
        return False


class Rate(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RateArticleSerializer

    def post(self, request, **kwargs):
        """
        rate user view
        """
        data = request.data.get('user', {})
        serializer = self.serializer_class(data=data)
        serializer.validate(data=data)
        serializer.is_valid(raise_exception=True)
        rate_article = None
        try:
            article = Article.objects.get(slug=data['slug'])
        except Exception:
            return Response({"response": "Article not found"},
                            status=status.HTTP_204_NO_CONTENT)
        rater = request.user
        try:
            rate_article = RateArticle.objects.get(
                rater=rater, article=article)
            rate_article.rate = data["rate"]
            rate_article.save()
            return Response({"response": "successfully rated"},
                            status=status.HTTP_200_OK)
        except Exception:
            RateArticle(
                rater=rater, article=article, rate=data["rate"]).save()
            return Response(data={"response": "sucessfully rated"},
                            status=status.HTTP_200_OK)
