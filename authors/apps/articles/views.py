from rest_framework import status
from ..authentication.renderers import UserJSONRenderer
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from .models import RateArticle, Article
from .serializers import RateArticleSerializer


class ArticleRate(APIView):
    """
    rate class article
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)

    def get(self, request, **kwargs):
        """
        rate user view
        """
        pk = kwargs.get("pk")
        rate_articles = None
        rate = 0
        try:
            rate_articles = RateArticle.objects.filter(article_id=int(pk))
        except Exception as e:
            raise serializers.ValidationError(
                str(e)
            )
        for rate_article in rate_articles:
            rate += rate_article.rate
        rate_value = 0
        if rate:
            rate_value = rate / len(rate_articles)
        return Response(data={"rates": round(rate_value, 2)},
                        status=status.HTTP_200_OK)


class Rate(CreateAPIView):
    """
    rate class article
    """
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
            return Response({"response": "sucessfully rated"},
                            status=status.HTTP_200_OK)
        except Exception:
            rate_article = RateArticle(
                rater=rater, article=article, rate=data["rate"])
            rate_article.save()
            return Response(data={"response": "sucessfully rated"},
                            status=status.HTTP_200_OK)
