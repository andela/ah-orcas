import os
import jwt
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.template.loader import render_to_string
from django.core.mail import send_mail

from authors.settings import EMAIL_HOST_USER
from authors.settings import DEFAULT_DOMAIN
from authors.settings import SECRET_KEY

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer
)
from .models import User


class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
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


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
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
    '''
    this class verifies a user based on the token sent to their email address.
    '''

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




