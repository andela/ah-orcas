from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly,\
    IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authors.apps.profiles.models import UserProfile
from authors.apps.profiles.renderers import ProfileJSONRenderer
from authors.apps.profiles.serializers import ProfileSerializer, \
    ProfileListSerializer


class ProfileRetrieveAPIView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def retrieve(self, request, username, *args, **kwargs):
        """
        Retrieves a given profile
        Throws an exception if the profile doesnt exist
        """
        try:
            # select_related method prevents unnecessary database calls.
            profile = UserProfile.objects.select_related('user').get(
                user__username=username
            )
        except Exception:
            return Response(
                {
                    'Message': 'There are no profiles found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.serializer_class(profile, context={
            'request': request
        })

        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateProfileAPIView(APIView):
    """
    This class handles updating a user's profile
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)

    def put(self, request, username):
        """
        Updates a given user profile
        """
        try:
            profile_data = request.data.get('user', {})
            serializer = ProfileSerializer(
                request.user.profile, data=profile_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response(
                {
                    'Message': 'There is no profile found'
                },
                status=status.HTTP_404_NOT_FOUND
            )


class ProfileListAPIView(ListAPIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, **kwargs):
        """
        Fetch all the available profiles
        """
        try:
            queryset = UserProfile.objects.all()
        except UserProfile.DoesNotExist:
            return Response(
                {
                    'Message': 'There are no profiles found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProfileListSerializer(queryset, many=True)
        profiles = Response({'profiles': serializer.data},
                            status=status.HTTP_200_OK)
        return profiles


class ProfileFollowAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def follow_unfollow(self, username, request, check, status_):
        follower = self.request.user.userprofile
        try:
            followee = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            return Response(
                {'Message': 'No profile with this username was found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if follower.pk is followee.pk:
            return Response({
                'Message': 'You can only follow others, not yourself'
            }, status=status.HTTP_409_CONFLICT)

        if check:
            follower.follow(followee)
        if not check:
            follower.unfollow(followee)

        serializer = self.serializer_class(followee, context={
            'request': request
        })
        return Response(serializer.data, status=status_)

    def post(self, request, username=None):
        """follow a profile with username 'username'"""
        return self.follow_unfollow(
            username, request, True, status.HTTP_201_CREATED)

    def delete(self, request, username=None):
        """un-follow a profile """
        return self.follow_unfollow(
            username, request, False, status.HTTP_200_OK)
