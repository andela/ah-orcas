import os
import jwt
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from rest_framework.views import APIView
from authors.settings import EMAIL_HOST_USER
from authors.settings import DEFAULT_DOMAIN
from authors.settings import SECRET_KEY
from django.template.loader import render_to_string
from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from .renderers import UserJSONRenderer
from .models import User
from .serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserSerializer,
    ResetPasswordSerializer,
    ForgetPasswordSerializer)


class RegistrationAPIView(CreateAPIView):
    """
    Register a new user
    """
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request, **kwargs):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
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
    """
    Login a registered user
    """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request, **kwargs):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


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
    """
    send password reset token to email
    """
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
        subject = "Reset Password"
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
        if not default_token_generator.check_token(user, token):
            return Response({"response": 'Invalid reset tokens'},
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
