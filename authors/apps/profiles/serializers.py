from .models import UserProfile
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False)
    image = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('username', 'bio', 'image', 'following',)
        read_only_fields = ('username',)

    def get_image(self, obj):
        if obj.image:
            return obj.image

        return 'null'

    def get_following(self, instance):
        """get the new profile instance which we want to follow"""
        # get the request context which contains the user
        request = self.context.get('request', None)
        if request is None:
            return False
        if request.user.is_authenticated:
            # obtain the profile instance from the request
            follower = request.user.userprofile
            followee = instance
            return follower.is_following(followee)


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
