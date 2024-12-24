from rest_framework.response import Response
from rest_framework import status
from functools import wraps
from django.db import connection

def isAuthorized(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        # Проверка наличия токена
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            return Response({"detail": "Authorization token is missing or invalid."}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]

        # Проверяем токен в таблице usertoken
        token_query = "SELECT user_id FROM usertoken WHERE key = %s"
        with connection.cursor() as cursor:
            cursor.execute(token_query, [token])
            result = cursor.fetchone()

        if not result:
            return Response({"detail": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = result[0]

        request.user_id = user_id
        return view_func(self, request, *args, **kwargs)
    return wrapper
