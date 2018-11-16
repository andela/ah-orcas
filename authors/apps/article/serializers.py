'''Serializers allow complex data
such as querysets and model instances
 to be converted to
native Python datatypes that can then
be easily rendered into JSON, XML or other content types.'''
import math

from rest_framework import serializers
from django.apps import apps
from rest_framework.validators import UniqueTogetherValidator

from authors.apps.profiles.models import UserProfile

from .models import RateArticle, Comments, CommentHistory, Favorite
from authors.apps.profiles.serializers import ProfileListSerializer

TABLE = apps.get_model('article', 'Article')
Profile = apps.get_model('profiles', 'UserProfile')

NAMESPACE = 'article'
fields = (
    'id',
    'slug',
    'image',
    'title',
    'description',
    'body',
    'user',
    'tags',
)


class ArticleSerializer(serializers.ModelSerializer):
    # add the return fields
    url = serializers.SerializerMethodField(read_only=True)
    facebook = serializers.SerializerMethodField(read_only=True)
    Linkedin = serializers.SerializerMethodField(read_only=True)
    twitter = serializers.SerializerMethodField(read_only=True)
    mail = serializers.SerializerMethodField(read_only=True)

    update_url = serializers.HyperlinkedIdentityField(
        view_name=NAMESPACE + ':update', lookup_field='slug')
    delete_url = serializers.HyperlinkedIdentityField(
        view_name=NAMESPACE + ':delete', lookup_field='slug')
    author = serializers.SerializerMethodField(read_only=True)

    def get_url(self, obj):
        request = self.context.get("request")
        return obj.api_url(request=request)

    def link_get(self, obj, link, args=None):
        """get url and append the link to url that you want to share"""
        request = self.context.get("request")
        if args is None:
            return link + obj.api_url(request=request)
        if args:
            return link + obj.api_url(request=request) + args

    def get_facebook(self, obj):
        """append facebook link."""
        link = 'https://www.facebook.com/sharer.php?u='
        return self.link_get(obj, link)

    def get_Linkedin(self, obj):
        """append linkedin link"""
        link = 'https://www.linkedin.com/shareArticle?mini=true&amp;url='
        return self.link_get(obj, link)

    def get_twitter(self, obj):
        """append twitter link"""
        link = 'https://twitter.com/share?url='
        args = '&amp;text=Amazing Read'
        return self.link_get(obj, link, args=args)

    def get_mail(self, obj):
        request = self.context.get("request")
        return 'mailto:?subject=New Article Alert&body={}'.format(
            obj.api_url(request=request))

    class Meta:
        model = TABLE

        fields = fields + ('author', 'update_url', 'delete_url', 'facebook',
                           'Linkedin',
                           'twitter',
                           'mail',
                           'url',
                           'favorited')

    def get_author(self, obj):
        try:
            serializer = ProfileListSerializer(
                instance=Profile.objects.get(user=obj.user)
            )
            return serializer.data
        except BaseException:
            return {}

    def get_favorited(self, instance):
        try:
            Favorite.objects.get(
                user=self.context["request"].user.id, article=instance.id)
            return True
        except BaseException:
            return False

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.body = validated_data.get('body', instance.body)
        if validated_data.get('image'):
            instance.image = validated_data.get('image', instance.image)

        instance.save()

        return instance


class ArticleCreateSerializer(serializers.ModelSerializer):
    time_to_read = serializers.CharField(required=False)
    images = serializers.ListField(child=serializers.CharField(
        max_length=1000), min_length=None, max_length=None, required=False)

    class Meta:
        model = TABLE

        fields = fields + ('images', 'time_to_read',)

    def get_time_to_read(self, body, images):
        """
        Calculates the time it takes to read a given article
        average reading time for plain text = 200wpm
        average reading time for images in articles = 15secs =0.25mins
        """

        image_view_time = 0
        if images:
            image_view_time = (len(images) * 0.25)
        time_taken = math.ceil((len(list(body)) / 250) + image_view_time)
        if time_taken <= 1:
            return str(time_taken) + 'min'
        return str(time_taken) + 'mins'

    def create(self, validated_data):
        instance = TABLE.objects.create(**validated_data)
        validated_data['slug'] = instance.slug
        validated_data['time_to_read'] = self.get_time_to_read(
            instance.body, validated_data.get('images'),)

        return validated_data


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


class ThreadSerializer(serializers.ModelSerializer):
    def to_representation(self, value):
        comment_details = self.parent.parent.__class__(
            value, context=self.context)
        return comment_details.data

    class Meta:
        model = Comments
        fields = '__all__'


class CommentsSerializer(serializers.ModelSerializer):
    """
    Serializer class for comments
    """
    author = serializers.SerializerMethodField(read_only=True)
    thread = ThreadSerializer(many=True, read_only=True)

    class Meta:
        model = Comments
        fields = ('id', 'body', 'author',
                  'created_at', 'updated_at', 'thread')

    def get_author(self, obj):
        try:
            profile = UserProfile.objects.get(user=obj.author)
            serializer = ProfileListSerializer(instance=profile)
            return serializer.data
        except Exception:
            return {}

    def create(self, validated_data):
        if self.context.get('parent'):
            parent = self.context.get('parent', None)
            instance = Comments.objects.create(parent=parent, **validated_data)
        else:
            instance = Comments()
            instance.author = self.context['request'].user
            instance.article = self.context['article']
            instance.body = validated_data.get('body')
            instance.save()
        return instance

    def update(self, instance, validated_data):
        obj = Comments.objects.only('id').get(id=instance.id)
        updated_comment = CommentHistory.objects.create(comment=instance.body,
                                                        original_comment=obj)
        updated_comment.save()
        instance.body = validated_data.get('body', instance.body)
        instance.save()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    """favorite serializer class"""
    class Meta:
        model = Favorite
        fields = ('article', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('article', 'user'),
                message="Article already favorited"
            )
        ]


class CommentHistorySerializer(serializers.ModelSerializer):
    """comment history serializer"""
    class Meta:
        model = CommentHistory
        fields = ('id', 'comment', 'date_created', 'original_comment')
