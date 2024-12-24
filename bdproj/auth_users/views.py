from re import I
import re
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils.generate_token import generate_token
from .utils.hash_password import hash_password, verify_password
from django.http import JsonResponse
from .serializers import UpdateUserSerializer, UserInfoSerializer, RegisterUserSerializer, LoginResponseSerializer
from .utils.required import isAuthorized
from .utils.check_unique import validate_unique_field

class RegisterUserAPIView(APIView):
    def post(self, request):
        data = request.data
        hashed_password = hash_password(data['password'])

        email_query = "SELECT id FROM users WHERE email = %s"
        with connection.cursor() as cursor:
            cursor.execute(email_query, [data['email']])
            existing_user = cursor.fetchone()

        if existing_user:
            return JsonResponse({"error": "Email already exists."}, status=400)
        
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
                return JsonResponse({"error": "Register error"}, status=400)
        

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
        
        user_id = user[0]


        query = "SELECT role_id FROM users WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query, [user_id])
            role_id = cursor.fetchone()
        
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
        serializer = LoginResponseSerializer({"token": token, "role_id": role_id[0]})
        return Response(serializer.data, status=200)
    

class UserInfoAPIView(APIView):

    @isAuthorized
    def get(self, request):

        user_id = request.user_id

        # Получаем информацию о пользователе
        user_query = """
                    SELECT 
                        u.id, 
                        u.fio, 
                        u.email, 
                        u.is_active, 
                        r.name AS role_name, 
                        l.name AS level_name, 
                        u.entrance_test
                    FROM 
                        users u
                    LEFT JOIN 
                        roles r ON u.role_id = r.id
                    LEFT JOIN 
                        levels l ON u.level_id = l.id
                    WHERE 
                        u.id = %s;
                    """
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
            "role": user[4],
            "level": user[5],
            "entrance_test": user[6]
        })

        return Response(serializer.data, status=200)
    
    @isAuthorized
    def put(self, request):
        user_id = request.user_id
        data = request.data

        get_password_query = "SELECT password FROM users WHERE id = %s;"
        with connection.cursor() as cursor:
            cursor.execute(get_password_query, [user_id])
            user_password = cursor.fetchone()

        if 'old_password' in data and 'new_password' in data:
            old_password = data['old_password']
            if not verify_password(old_password, user_password):
                return JsonResponse({"error": "The old password is incorrect."}, status=400)      
        
    
        # Проверка уникальности email (если email передан)
        email = data["email"]
        if email and not validate_unique_field(
            "users", "email", email, exclude_id=user_id
        ):
            return JsonResponse({"error": "Email already exists."}, status=400)

        # Динамическое построение полей для обновления
        update_fields = []
        values = []

        if 'fio' in data:
            update_fields.append("fio = %s")
            values.append(data['fio'])
        if 'email' in data:
            update_fields.append("email = %s")
            values.append(data['email'])

        if 'new_password' in data and 'old_password' in data:
            hashed_new_password = hash_password(data['new_password'])
            update_fields.append("password = %s")
            values.append(hashed_new_password)

        # Формирование SQL-запроса
        query = f"""
        UPDATE users
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, fio, email;
        """
        values.append(user_id)

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                updated_user = cursor.fetchone()
        except Exception as e:
            return JsonResponse({"error": f"Unable to update user: {e}"}, status=400)

        # Сериализация данных
        serializer = UpdateUserSerializer({
            "id": updated_user[0],
            "fio": updated_user[1],
            "email": updated_user[2],
        })

        return JsonResponse(serializer.data, status=200)