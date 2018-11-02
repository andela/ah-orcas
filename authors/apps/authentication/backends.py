# import jwt
#
# from django.conf import settings
#
import jwt
from django.http import HttpResponse
from rest_framework import authentication, exceptions
#
# from .models import User
from rest_framework.authentication import get_authorization_header

from authors import settings
from authors.apps.authentication.models import User


class JWTAuthentication(authentication.BaseAuthentication):
    """Validate JWT token"""

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'bearer':
            return None

        if len(auth) == 1 or len(auth) > 2:
            raise exceptions.AuthenticationFailed('Invalid token header')

        try:
            token = auth[1]
            if token == "null":
                raise exceptions.AuthenticationFailed('Invalid token.')
        except UnicodeError:
            raise exceptions.AuthenticationFailed('Invalid token header.')
        return self.auth_credentials(token)

    def auth_credentials(self, token):
        payload = jwt.decode(token, settings.SECRET_KEY)
        user_id = payload['id']
        try:
            user = User.objects.get(id=user_id)
        except jwt.exceptions:
            return HttpResponse({'error': 'Invalid token'}, status='403')
        except User.DoesNotExist:
            m = HttpResponse({'error': 'Internal server error'}, status='500')
            return m

        return user, token
