from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Bookmark


class BookmarkSerializer(serializers.ModelSerializer):
    """Bookmark serializer class"""
    class Meta:
        model = Bookmark
        fields = ('article', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Bookmark.objects.all(),
                fields=('article', 'user'),
                message="Article already bookmarked"
            )
        ]
