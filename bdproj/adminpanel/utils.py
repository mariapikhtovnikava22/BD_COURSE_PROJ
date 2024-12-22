from rest_framework.response import Response
from rest_framework import status
from functools import wraps
from django.db import connection

def admin_required(view_func):
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

        # Проверяем роль пользователя
        role_query = "SELECT role_id FROM users WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(role_query, [user_id])
            user_role = cursor.fetchone()

        if not user_role or user_role[0] != 1:  # Предполагается, что роль администратора имеет ID = 1
            return Response({"detail": "You don't have administrator rights."}, status=status.HTTP_403_FORBIDDEN)

        # Сохраняем user_id в request для дальнейшего использования
        request.user_id = user_id
        return view_func(self, request, *args, **kwargs)
    return wrapper
