from .serializers import (
    ArticleReportSerializer
)
from rest_framework.generics import (
    CreateAPIView,
)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
)


class ArticleReportAPIView(CreateAPIView):
    serializer_class = ArticleReportSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
