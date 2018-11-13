from .serializers import (
    TABLE,
    ArticleSerializer,
    ArticleCreateSerializer,
    RateArticleSerializer
)
from rest_framework.views import APIView
from ..core.permissions import IsOwnerOrReadOnly
from ..authentication.renderers import UserJSONRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from authors import settings
from django.db.models import Q
from rest_framework.generics import (
    ListAPIView, CreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated
)
from .models import (RateArticle,
                     Article)

LOOKUP_FIELD = 'slug'


class StandardPagination(PageNumberPagination):
    page_size = settings.PAGE_SIZE
    page_size_query_param = 'page_size'


class ArticleListAPIView(ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ArticleSerializer
    pagination_class = StandardPagination

    def get_queryset(self, *args, **kwargs):
        queryset_list = TABLE.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(title__icontains=query) |
                Q(slug__icontains=query) |
                Q(description__icontains=query)
            )

        return queryset_list.order_by('-id')


class ArticleCreateAPIView(CreateAPIView):
    serializer_class = ArticleCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = TABLE.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = TABLE.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = LOOKUP_FIELD

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class ArticleRate(APIView):
    """
    rate class article
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
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
            RateArticle(
                rater=rater, article=article, rate=data["rate"]).save()
            return Response(data={"response": "sucessfully rated"},
                            status=status.HTTP_200_OK)
