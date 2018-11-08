from rest_framework import serializers
from .models import RateArticle


class RateArticleSerializer(serializers.ModelSerializer):
    """
    validate rate article
    """
    slug = serializers.SlugField()
    rate = serializers.IntegerField()

    def validate(self, data):
        rate = data['rate']
        if not rate > 0 or not rate <= 5:
            raise serializers.ValidationError(
                'invalid rate value should be > 0 or <=5')

        return data

    class Meta:
        model = RateArticle
        fields = ("slug", "rate")
