from .models import UserProfile
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False)
    image = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('username', 'bio', 'image',)
        read_only_fields = ('username',)

    def get_image(self, obj):
        if obj.image:
            return obj.image

        return 'null'


class ProfileListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    bio = serializers.CharField(allow_blank=True, required=False)
    image = serializers.SerializerMethodField(default=None)

    class Meta:
        model = UserProfile
        fields = ('username', 'bio', 'image', )

    def get_image(self, obj):
        if obj.image:
            return obj.image
        return 'null'
