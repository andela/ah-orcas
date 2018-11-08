import os
import jwt
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework import generics, serializers, status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from social_core.backends.oauth import BaseOAuth1, BaseOAuth2
from social_core.exceptions import AuthAlreadyAssociated, MissingBackend
from social_django.utils import load_strategy, load_backend
from authors.settings import DEFAULT_DOMAIN, EMAIL_HOST_USER, SECRET_KEY
from .models import User
from .renderers import UserJSONRenderer
from .serializers import (LoginSerializer,
                          RegistrationSerializer,
                          UserSerializer,
                          ResetPasswordSerializer,
                          ForgetPasswordSerializer,
                          SocialSignUpSerializer)


class RegistrationAPIView(CreateAPIView):
    """Register a new user """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request, **kwargs):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        token = serializer.data['token']
        verify_link = str(DEFAULT_DOMAIN) + "api/users/verify/" + str(token)
        body = render_to_string('email_confirm.html', {
            'link': verify_link,
            'username': user['username'],
            'ENVIRONMENT': os.getenv('DEFAULT_DOMAIN')
        })
        send_mail(
            'Authors Heaven Acount activation!',
            'Verify your account.',
            EMAIL_HOST_USER,
            [user['email']],
            html_message=body,
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(CreateAPIView):
    """Login a registered user """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request, **kwargs):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserUpdateAPIView(UpdateAPIView):
    """
    Updates the user profile
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def put(self, request, *args, **kwargs):
        """User profile update"""
        user_data = request.data.get('user', {})

        serializer_data = {
            'username': user_data.get('username', request.user.username),
            'email': user_data.get('email', request.user.email),
            'bio': user_data.get('bio', request.user.userprofile.bio),
            'image': user_data.get('image', request.user.userprofile.image)
        }
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer_data, status=status.HTTP_200_OK)


class VerifyAPIView(APIView):
    """
    Verifies a user based on the token sent to their email address.
    """
    def get(self, request, token):
        try:
            user = jwt.decode(token, SECRET_KEY)
            user_exist = User.objects.get(id=user['id'])
            user_exist.is_confirmed_email = True
            user_exist.save()
            user_exist.save()
            return Response(
                data={
                    "Message": "You have succesfully verified your account"},
                status=status.HTTP_200_OK)
        except Exception:
            return Response(data={"Message": "Link provided is not valid"},
                            status=status.HTTP_401_UNAUTHORIZED)


class ForgetPassword(APIView):
    """send password reset token to email"""
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = ForgetPasswordSerializer

    def post(self, request):
        """
        this method sends reset token in a link to a registered user
        """
        data = request.data.get('user', {})
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=data['email'])
        except (User.DoesNotExist):
            raise serializers.ValidationError(
                'A user with this email was not found.'
            )
        token = default_token_generator.make_token(user)
        domain = get_current_site(request).domain
        hashed_email = jwt.encode(
            {"email": data['email']}, SECRET_KEY, algorithm='HS256')
        our_link = "http://" + domain + '/api/users/reset/' + \
            hashed_email.decode('UTF-8') + "/" + token
        msg = render_to_string('activate_account.html', {
            'user': user.username,
            "link": our_link
        })
        send_mail('Authors Heaven Password Reset!',
                  'Password Reset',
                  EMAIL_HOST_USER,
                  [data['email']],
                  html_message=msg,
                  fail_silently=False)

        return Response(
            {"response": "Confirm your email to continue"},
            status=status.HTTP_200_OK)


class ResetPassword(APIView):
    """
    reset password class
    """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = ResetPasswordSerializer

    def get(self, request, **kwargs):
        """verify the token on get"""
        token = kwargs.get('token')
        hashed_email = kwargs.get('hashed_email')
        data = jwt.decode(hashed_email, SECRET_KEY, algorithm='HS256')
        user = User.objects.get(email=data['email'])
        if not default_token_generator.check_token(user, token):
            return Response({"response": 'Invalid reset tokens'},
                            status=status.HTTP_401_UNAUTHORIZED)
        return Response(
            {"response": "email confirmed successfully",
             "email": data["email"]})

    def put(self, request, **kwargs):
        """
        actually password reset is done here
        """
        token = kwargs.get('token')
        hashed_email = kwargs.get('hashed_email')
        data = jwt.decode(hashed_email, SECRET_KEY, algorithm='HS256')
        user = None
        try:
            user = User.objects.get(email=data['email'])
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"response": 'A user with this email was not found.'})
        is_valid = default_token_generator.check_token(user, token)
        if not is_valid:
            return Response({"response": 'Token expired'},
                            status=status.HTTP_401_UNAUTHORIZED)
        new_password = request.data.get('user')
        user.set_password(new_password)
        user.save()
        msg = render_to_string('alert_reset_password.html', {
            'user': user.username
        })
        send_mail('Authors Heaven Password Reset!',
                  'Reset password.',
                  EMAIL_HOST_USER,
                  [data['email']],
                  html_message=msg,
                  fail_silently=False)
        return Response({'response': 'password successfully changed'})


class SocialAuthView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SocialSignUpSerializer
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)

    def create(self, request, *args, **kwargs):
        """
        Override `create` instead of `perform_create` to access request
        request is necessary for `load_strategy`
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return self.create_token(request, serializer)

    def create_token(self, request, serializer):
        provider = request.data['provider']
        # passing `request` to `load_strategy`,
        # `strategy` is a PSA concept for referencing Python frameworks
        strategy = load_strategy(request)
        # get backend corresponding to our user's social auth provider
        # i.e. Google, Facebook, Twitter
        try:
            backend = load_backend(
                strategy=strategy, name=provider, redirect_uri=None)
        except MissingBackend as e:
            return Response({
                "errors": {
                    "provider": ["Provider not found.", str(e)]
                }

            }, status=status.HTTP_404_NOT_FOUND)

        if isinstance(backend, BaseOAuth1):
            try:
                # Twitter uses OAuth1 and requires that you also pass
                # an `oauth_token_secret` with your authentication request
                token = {
                    'oauth_token': serializer.data['access_token'],
                    'oauth_token_secret': request.data['access_token_secret'],
                }
            except KeyError:
                return Response({
                    "errors": "provide access_token and/or access_token_secret"

                }, status=status.HTTP_400_BAD_REQUEST)

        elif isinstance(backend, BaseOAuth2):
            # only access token required for oauth2
            token = serializer.data['access_token']

        return self.get_auth_user(request, backend, token, provider)

    def get_auth_user(self, request, backend, token, provider):
        # If this request is made with an authenticated user,
        #  try to associate a social account with it
        authed_user = request.user if not request.user.is_anonymous else None

        try:
            # if `authed_user` is None,
            #   python-social-auth will make a new user,
            # else
            #   this social account will be associated with the user parsed
            user = backend.do_auth(token, user=authed_user)
        except AuthAlreadyAssociated:
            return Response({
                "errors": "That social media account is already in use"
            }, status=status.HTTP_409_CONFLICT)

        return self.serialize_user(user, provider, token)

    def serialize_user(self, user, provider, token):
        if user and user.is_active:
            # if the access token was set to an empty string,
            # then save the access token from the request
            serializer = UserSerializer(user)
            auth_created = user.social_auth.get(provider=provider)
            if not auth_created.extra_data['access_token']:
                auth_created.extra_data['access_token'] = token
                auth_created.save()

            # Set instance since we are not calling `serializer.save()`
            serializer.instance = user
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)
        else:
            return Response({"errors": "Error with social authentication"},
                            status=status.HTTP_400_BAD_REQUEST)
