from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from authors.apps.article.renderers import FavoriteJSONRenderer
from authors.apps.article.serializers import FavoriteSerializer,\
    ArticleSerializer
from .models import (Article,
                     LikeDislikeArticle,
                     Favorite,
                     check_article)


LOOKUP_FIELD = 'slug'
no_article = "No article found"
undisliked_response = "article successfully undisliked"
disliked_article_response = "article successfully disliked"


def get_article(kwargs):
    """
    query article
    """
    slug = kwargs.get('slug')
    article = Article.objects.get(slug=slug)
    return article


class Like(APIView):
    """
    Like views
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, **kwargs):
        """
        Like an article.
        """
        article = None
        try:
            slug = kwargs.get('slug')
            article = Article.objects.get(slug=slug)
            liker = request.user
        except Exception:
            return Response({"response": "No article found"},
                            status=status.HTTP_204_NO_CONTENT)
        try:
            like = LikeDislikeArticle.objects.get(
                article=article, liker=liker)
            if like.is_liked:
                like.is_liked = False
                like.save()
                return Response(
                    {"response": "article successfully unliked"},
                    status=status.HTTP_200_OK)
            like.is_disliked = False
            like.is_liked = True
            like.save()
            return Response(
                {"response": "article successfully liked"},
                status=status.HTTP_200_OK)
        except Exception:
            like = LikeDislikeArticle(
                liker=liker,
                article=article,
                is_liked=True)
            like.save()
            return Response(
                {"response": "article successfully liked"},
                status=status.HTTP_200_OK)

    def get(self, request, **kwargs):
        """
        Return likes of an article
        """

        likes = None
        slug = kwargs.get('slug')
        try:
            article = Article.objects.get(slug=slug)
        except Exception:
            return Response({"response": no_article},
                            status=status.HTTP_204_NO_CONTENT)
        likes = LikeDislikeArticle.objects.filter(article=article)
        return Response({"response": len(
            [like for like in likes if like.is_liked])},
            status=status.HTTP_200_OK)


class Dislike(APIView):
    """
    Dislike views
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        """
        Return dislikes of an article
        """

        try:
            disliked_article = get_article(kwargs)
        except Exception:
            return Response({"response": "No article found"},
                            status=status.HTTP_204_NO_CONTENT)
        dislikes = LikeDislikeArticle.objects.filter(
            article=disliked_article)
        dislikes_number = [
            dislike for dislike in dislikes if dislike.is_disliked]
        return Response({"response": len(dislikes_number)},
                        status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        """
        Like an article.
        """
        disliked_article = None
        disliker = None
        try:
            disliked_article = get_article(kwargs)
            disliker = request.user
        except Exception:
            return Response({"response": "No article found"},
                            status=status.HTTP_204_NO_CONTENT)

        try:
            dislike = LikeDislikeArticle.objects.get(
                article=disliked_article,
                liker=disliker)
            if dislike.is_disliked:
                dislike.is_disliked = False
                dislike.save()
                return Response(
                    {"response": undisliked_response},
                    status=status.HTTP_200_OK)
            dislike.is_liked = False
            dislike.is_disliked = True
            dislike.save()
            return Response(
                {"response": disliked_article_response},
                status=status.HTTP_200_OK)
        except Exception as e:
            LikeDislikeArticle(
                liker=disliker,
                article=disliked_article,
                is_disliked=True).save()
            return Response(
                {"response": "article successfully disliked"},
                status=status.HTTP_200_OK)


class FavoriteAPIView(APIView):
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Favorite.objects.all()
    renderer_classes = (FavoriteJSONRenderer,)

    def post(self, request, slug):
        """favorite article view class"""
        article = check_article(slug)
        if article is None:
            return Response({"Message": [
                "That article does not exist"
            ]}, status.HTTP_204_NO_CONTENT)

        favorite = dict()
        favorite["user"] = request.user.id
        # import pdb; pdb.set_trace()
        favorite["article"] = article.pk
        serializer = self.serializer_class(data=favorite)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        article_serializer = ArticleSerializer(
            instance=article, context={'request': request})
        data = dict(article=article_serializer.data)
        data["article"]["favorited"] = True
        data["message"] = "favorited"
        return Response(data, status.HTTP_200_OK)

    def delete(self, request, slug):
        """unfavorite an article"""

        article = check_article(slug)

        if article is None:
            return Response({"Message": [
                "That article does not exist"
            ]}, status.HTTP_204_NO_CONTENT)

        try:
            favorite = Favorite.objects.get(
                user=request.user.id, article=article.pk)
        except Favorite.DoesNotExist:
            return Response(
                {"Message": "You have not favorited this article yet"},
                status.HTTP_409_CONFLICT)
        favorite.delete()
        article_serializer = ArticleSerializer(
            instance=article, context={'request': request})
        data = dict(article=article_serializer.data)
        data["message"] = "unfavorited"
        return Response(data, status.HTTP_200_OK)
