from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils.generate_token import generate_token
from .utils.hash_password import hash_password, verify_password
from django.http import JsonResponse
from .serializers import UserInfoSerializer, RegisterUserSerializer, LoginResponseSerializer


class RegisterUserAPIView(APIView):
    def post(self, request):
        data = request.data
        hashed_password = hash_password(data['password'])

        # SQL-запрос для вставки нового пользователя
        query = """
        INSERT INTO users (fio, email, password)
        VALUES (%s, %s, %s)
        RETURNING id, fio, email;
        """
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, [
                    data['fio'],
                    data['email'],
                    hashed_password,
                ])
                user = cursor.fetchone()
            except Exception as e:
                return JsonResponse({"error": "Email already exists or invalid data."}, status=400)

        # Использование сериализатора
        serializer = RegisterUserSerializer({
            "id": user[0],
            "fio": user[1],
            "email": user[2],
        })
        return Response(serializer.data, status=201)

class LoginUserAPIView(APIView):
    def post(self, request):
        data = request.data

        # SQL-запрос для получения пользователя по email
        query = "SELECT id, password FROM users WHERE email = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, [data['email']])
            user = cursor.fetchone()

        if not user or not verify_password(data['password'], user[1]):
            return JsonResponse({"error": "Invalid email or password."}, status=401)

        # Генерация токена
        token = generate_token()
        token_query = """
        INSERT INTO usertoken (key, user_id) 
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO UPDATE SET key = EXCLUDED.key 
        RETURNING key
        """
        with connection.cursor() as cursor:
            cursor.execute(token_query, [token, user[0]])
            token = cursor.fetchone()[0]

        # Использование сериализатора
        serializer = LoginResponseSerializer({"token": token})
        return Response(serializer.data, status=200)
    

class UserInfoAPIView(APIView):
    def get(self, request):
        # Получение токена из заголовка Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            return JsonResponse({"error": "Authorization token is missing or invalid."}, status=401)

        token = auth_header.split(' ')[1]  # Извлекаем сам токен

        # Проверяем токен в таблице authtoken
        token_query = "SELECT user_id FROM usertoken WHERE key = %s"
        with connection.cursor() as cursor:
            cursor.execute(token_query, [token])
            result = cursor.fetchone()

        if not result:
            return JsonResponse({"error": "Invalid token."}, status=401)

        user_id = result[0]

        # Получаем информацию о пользователе
        user_query = "SELECT id, fio, email, is_active FROM users WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(user_query, [user_id])
            user = cursor.fetchone()

        if not user:
            return JsonResponse({"error": "User not found."}, status=404)

        # Сериализация данных
        serializer = UserInfoSerializer({
            "id": user[0],
            "fio": user[1],
            "email": user[2],
            "is_active": user[3],
        })

        return Response(serializer.data, status=200)