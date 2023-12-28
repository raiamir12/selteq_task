# tasks/middleware.py
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseForbidden


class CustomAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization', '')

        if auth_header:
            auth_parts = auth_header.split(' ')

            if len(auth_parts) == 2 and auth_parts[0].lower() == 'token':
                auth_token = auth_parts[1]

                try:
                    token = Token.objects.get(key=auth_token)
                    request.user = token.user
                except Token.DoesNotExist:
                    request.user = AnonymousUser()
                except Exception as e:

                    pass

        response = self.get_response(request)
        return response
