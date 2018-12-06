from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from authors.apps.bookmark.serializers import BookmarkSerializer
from authors.apps.article.serializers import ArticleSerializer
from authors.apps.article.models import check_article
from .models import Bookmark


class BookmarkAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BookmarkSerializer
    queryset = Bookmark.objects.all()

    def post(self, request, slug):
        """Bookmark article"""
        article = check_article(slug)
        if article is None:
            return Response({"Message": [
                "That article does not exist"
            ]}, status.HTTP_204_NO_CONTENT)

        bookmark = dict()
        bookmark["user"] = request.user.id
        bookmark["article"] = article.pk
        serializer = self.serializer_class(data=bookmark)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        article_serializer = ArticleSerializer(
            instance=article, context={'request': request})
        data = dict(article=article_serializer.data)
        data["article"]["bookmarked"] = True
        data["message"] = "bookmarked"
        return Response(data, status.HTTP_200_OK)

    def delete(self, request, slug):
        """unbookmark an article"""
        article = check_article(slug)
        if article is None:
            return Response({"Message": [
                "That article does not exist"
            ]}, status.HTTP_204_NO_CONTENT)
        try:
            bookmark = Bookmark.objects.get(
                user=request.user.id, article=article.pk)
        except Bookmark.DoesNotExist:
            return Response(
                {"Message": "You have not bookmarked this article yet"},
                status.HTTP_409_CONFLICT)
        bookmark.delete()
        article_serializer = ArticleSerializer(
            instance=article, context={'request': request})
        data = dict(article=article_serializer.data)
        data["message"] = "bookmark deleted"
        return Response(data, status.HTTP_200_OK)
