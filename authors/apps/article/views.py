from rest_framework.generics import (
    ListAPIView, CreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveAPIView,
    DestroyAPIView,
    get_object_or_404, RetrieveUpdateDestroyAPIView)
from django.db.models import Q
from authors import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, generics, permissions, serializers
from rest_framework.response import Response
from ..core.permissions import IsOwnerOrReadOnly
from django.http import Http404
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticatedOrReadOnly,
    IsAuthenticated)
from rest_framework.views import APIView
from authors.apps.article.models import (
    Article,
    Comments,
    CommentHistory)
from authors.apps.article.renderers import CommentsRenderer
from .serializers import (TABLE,
    ArticleSerializer,
    ArticleCreateSerializer,
    CommentsSerializer,
    CommentHistorySerializer, )
from ..core.permissions import IsOwnerOrReadOnly
from ..authentication.renderers import UserJSONRenderer
from rest_framework.response import Response
from rest_framework import status, generics, permissions, serializers
from rest_framework.pagination import PageNumberPagination
from authors import settings
from django.db.models import Q
from rest_framework.generics import (
    ListAPIView, CreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveAPIView,
    DestroyAPIView,
    get_object_or_404,
    RetrieveUpdateDestroyAPIView)
from .models import RateArticle
from.send_notifiactions import (
    send_article_notification,
    send_followers_notification)


LOOKUP_FIELD = 'slug'


class StandardPagination(PageNumberPagination):
    page_size = settings.PAGE_SIZE
    page_size_query_param = 'page_size'


class ArticleListAPIView(ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ArticleSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Article.objects.all()
        username = self.request.query_params.get('author', None)
        if username is not None:
            queryset = queryset.filter(user__username__iexact=username)
        tags = self.request.query_params.get('tags', None)
        if tags is not None:
            tags = tags.split(',')
            queryset = queryset.filter(tags__overlap=tags)
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(slug__icontains=search) |
                Q(description__icontains=search) |
                Q(body__contains=search)
            )
        return queryset


class ArticleCreateAPIView(CreateAPIView):
    serializer_class = ArticleCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = TABLE.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        send_followers_notification(instance,
                                    self.request.user)


class ArticleDetailAPIView(RetrieveAPIView):
    queryset = TABLE.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = LOOKUP_FIELD

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class ArticleDeleteAPIView(DestroyAPIView):
    queryset = TABLE.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = ArticleSerializer
    lookup_field = LOOKUP_FIELD


class ArticleUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]
    queryset = TABLE.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = LOOKUP_FIELD

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class ArticleRate(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (UserJSONRenderer,)

    def get(self, request, **kwargs):
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


class CommentsListCreateView(generics.ListCreateAPIView):
    """
   This class handles the endpoints for creating and listing comments
    """
    queryset = Comments.objects.all()

    serializer_class = CommentsSerializer
    renderer_classes = (CommentsRenderer,)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, slug=None, *args, **kwargs):
        serializer_context = {
            'request': request,
            'author': request.user,
            'article': get_object_or_404(Article, slug=self.kwargs["slug"])
        }
        data = request.data.get('comments', {})
        serializer = self.serializer_class(
            data=data, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_article_notification(self.kwargs["slug"], data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, slug=None, **kwargs):
        article = get_object_or_404(Article, slug=self.kwargs["slug"])
        comment = Comments.objects.filter(article__id=article.id)
        serializer = self.serializer_class(comment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentsUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView, CreateAPIView):
    query = Article.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentsSerializer
    serializer_history = CommentHistorySerializer

    def get_object(self):
        article = get_object_or_404(Article, slug=self.kwargs["slug"])
        comments = Comments.objects.filter(article__id=article.id)
        if not comments:
            raise Http404
        for comment in comments:
            new_comment = get_object_or_404(
                Comments, pk=self.kwargs["comment_id"])
            if comment.id == new_comment.id:
                return comment

    def create(self, request, slug=None, pk=None, **kwargs):
        """
        Handles the creation of replies
        """
        data = request.data
        context = {'request': request}
        comment = self.get_object()
        context['parent'] = Comments.objects.get(pk=comment.id)

        if context['parent']:
            serializer = self.serializer_class(data=data, context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save(author=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"Message": "Comment requested was not found"})

    def delete(self, request, slug=None, pk=None, **kwargs):
        """This function will delete a specific comment"""
        article = get_object_or_404(Article, slug=self.kwargs["slug"])
        comment = Comments.objects.filter(pk=article.id)
        if comment is None:
            resp = Response({"message": " The Comment does Not Exist"},
                            status=status.HTTP_404_NOT_FOUND)
            return resp
        comment.delete()
        return Response(
            {"message": {"Comment deleted successfully"}}, status.HTTP_200_OK)


class ArticleTags(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ArticleSerializer

    def put(self, request, **kwargs):
        data = request.data.get('article')
        try:
            article = Article.objects.get(slug=kwargs.get('slug', None))
        except Article.DoesNotExist:
            return Response({'response': 'Article not found'},
                            status=status.HTTP_404_NOT_FOUND)

        if request.user.username == article.user.username:
            tags = data['tags']
            if article.tags is None:
                article.tags = tags
            else:
                article.tags.extend(tags)
                # remove duplicates
                article.tags = list(set(article.tags))
            article.save()
            return Response({'response': 'Successfully added tags'},
                            status=status.HTTP_200_OK)

        return Response(
            {'response': 'You do not have permission to tag this article'},
            status.HTTP_403_FORBIDDEN)


class CommentHistoryAPIView(generics.ListAPIView):
    """This class gets all comment edit history"""
    lookup_url_kwarg = 'pk'
    serializer_class = CommentHistorySerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        Overrides the default GET request from ListAPIView
        Returns all comment edits for a particular comment
        """

        try:
            comment = Comments.objects.get(pk=kwargs['id'])
        except Comments.DoesNotExist:
            return Response(
                {"message": "Comment not found"},
                status=status.HTTP_404_NOT_FOUND)
        """If the queryset is populated, this returns a 200 OK response"""
        self.queryset = CommentHistory.objects.filter(original_comment=comment)
        return generics.ListAPIView.list(self, request, *args, **kwargs)
