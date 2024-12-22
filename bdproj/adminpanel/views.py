from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from auth_users.utils.generate_token import generate_token
from auth_users.utils.hash_password import hash_password, verify_password
from django.http import JsonResponse
from .serializers import UserSerializer, RoleSerializer, LevelSerializer
from .utils import admin_required

class AdminUserAPIView(APIView):

    @admin_required
    def get(self, request, user_id=None):
        """
        Получение списка всех пользователей или информации о конкретном пользователе.
        """
        if user_id:
            # SQL-запрос для получения информации о конкретном пользователе
            query = """
            SELECT 
                u.id, u.fio, u.email, u.is_active, 
                r.name AS role, 
                l.name AS level, 
                u.entrance_test
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            LEFT JOIN levels l ON u.level_id = l.id
            WHERE u.id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(query, [user_id])
                user = cursor.fetchone()

            if not user:
                return Response({"detail": "User not found."}, status=404)

            # Использование сериализатора
            serializer = UserSerializer({
                "id": user[0],
                "fio": user[1],
                "email": user[2],
                "is_active": user[3],
                "role": user[4],
                "level": user[5],
                "entrance_test": user[6],
            })
            return Response(serializer.data, status=200)
        else:
            # SQL-запрос для получения всех пользователей
            query = """
            SELECT 
                u.id, u.fio, u.email, u.is_active, 
                r.name AS role, 
                l.name AS level, 
                u.entrance_test
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            LEFT JOIN levels l ON u.level_id = l.id
            """
            with connection.cursor() as cursor:
                cursor.execute(query)
                users = cursor.fetchall()

            # Формируем список пользователей
            users_data = [
                {
                    "id": user[0],
                    "fio": user[1],
                    "email": user[2],
                    "is_active": user[3],
                    "role": user[4],
                    "level": user[5],
                    "entrance_test": user[6],
                }
                for user in users
            ]
            return Response(users_data, status=200)

    @admin_required
    def post(self, request):
        """
        Создание нового пользователя.
        """
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
        INSERT INTO users (fio, email, password, role_id, level_id, is_active, entrance_test)
        VALUES (%s, %s, %s, 
                (SELECT id FROM roles WHERE name = %s), 
                (SELECT id FROM levels WHERE name = %s), 
                %s, %s)
        RETURNING id, fio, email, is_active, 
                  (SELECT name FROM roles WHERE id = role_id), 
                  (SELECT name FROM levels WHERE id = level_id), 
                  entrance_test;
        """
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, [
                    data['fio'],
                    data['email'],
                    hashed_password,
                    data['role'],  # Название роли
                    data.get('level'),  # Название уровня (может быть NULL)
                    data.get('is_active', True),
                    data.get('entrance_test', False),
                ])
                user = cursor.fetchone()
            except Exception as e:
                return Response({"detail": f"Unable to create user. {e}"}, status=400)


        # Использование сериализатора
        serializer = UserSerializer({
            "id": user[0],
            "fio": user[1],
            "email": user[2],
            "is_active": user[3],
            "role": user[4],
            "level": user[5],
            "entrance_test": user[6],
        })
        return Response(serializer.data, status=201)
    
    @admin_required
    def put(self, request, user_id=None):
        """
        Обновление информации о пользователе.
        """
        if not user_id:
            return Response({"detail": "User ID is required in URL."}, status=400)
        

        user_check_query = "SELECT id FROM users WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(user_check_query, [user_id])
            existing_user = cursor.fetchone()

        if not existing_user:
            return Response({"detail": "User with the given ID does not exist."}, status=404)

        data = request.data

        # Проверка уникальности email (если email передан)
        email = data.get('email')
        if email:
            email_query = "SELECT id FROM users WHERE email = %s AND id != %s"
            with connection.cursor() as cursor:
                cursor.execute(email_query, [email, user_id])
                existing_user = cursor.fetchone()

            if existing_user:
                return JsonResponse({"error": "Email already exists."}, status=400)

        # Динамическое построение SQL-запроса для обновления
        update_fields = []
        values = []

        if 'fio' in data:
            update_fields.append("fio = %s")
            values.append(data['fio'])

        if 'email' in data:
            update_fields.append("email = %s")
            values.append(data['email'])

        if 'role' in data:
            update_fields.append("role_id = (SELECT id FROM roles WHERE name = %s)")
            values.append(data['role'])

        if 'level' in data:
            update_fields.append("level_id = (SELECT id FROM levels WHERE name = %s)")
            values.append(data['level'])

        if 'is_active' in data:
            update_fields.append("is_active = %s")
            values.append(data['is_active'])

        if 'entrance_test' in data:
            update_fields.append("entrance_test = %s")
            values.append(data['entrance_test'])

        # Если нет данных для обновления, вернуть ошибку
        if not update_fields:
            return Response({"detail": "No fields to update."}, status=400)

        # Формируем запрос для обновления
        query = f"""
        UPDATE users
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, fio, email, is_active, 
                (SELECT name FROM roles WHERE id = role_id), 
                (SELECT name FROM levels WHERE id = level_id), 
                entrance_test;
        """
        values.append(user_id)  # Добавляем user_id в параметры

        # Выполнение запроса
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, values)
                user = cursor.fetchone()
            except Exception as e:
                return Response({"detail": f"Unable to update user. {e}"}, status=400)

        # Использование сериализатора
        serializer = UserSerializer({
            "id": user[0],
            "fio": user[1],
            "email": user[2],
            "is_active": user[3],
            "role": user[4],
            "level": user[5],
            "entrance_test": user[6],
        })
        return Response(serializer.data, status=200)


    @admin_required
    def delete(self, request, user_id=None):
        """
        Удаление пользователя.
        """
        if not user_id:
            return Response({"detail": "User ID is required in URL."}, status=400)
        
        user_check_query = "SELECT id FROM users WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(user_check_query, [user_id])
            existing_user = cursor.fetchone()

        if not existing_user:
            return Response({"detail": "User with the given ID does not exist."}, status=404)

        # SQL-запрос для удаления пользователя
        query = "DELETE FROM users WHERE id = %s"
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, [user_id])
            except Exception as e:
                return Response({"detail": f"Unable to delete user. {e}"}, status=400)

        return Response({"detail": "User deleted successfully."}, status=200)




class RoleAPIView(APIView):

    @admin_required
    def post(self, request):
        """
        Создание новой роли.
        """
        data = request.data

        # Проверка на существующее имя роли
        name_query = "SELECT id FROM roles WHERE name = %s"
        with connection.cursor() as cursor:
            cursor.execute(name_query, [data['name']])
            existing_name = cursor.fetchone()

        if existing_name:
            return JsonResponse({"error": "Role name already exists."}, status=400)

        # Вставка новой роли
        query = "INSERT INTO roles (name) VALUES (%s) RETURNING id, name;"
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, [data['name']])
                role = cursor.fetchone()
            except Exception as e:
                return JsonResponse({"error": "Unable to create role. " + str(e)}, status=400)

        return JsonResponse({"id": role[0], "name": role[1]}, status=201)

    @admin_required
    def get(self, request):
        """
        Получение списка всех ролей.
        """
        query = "SELECT id, name FROM roles ORDER BY id;"
        with connection.cursor() as cursor:
            cursor.execute(query)
            roles = cursor.fetchall()

        return JsonResponse(
            [{"id": role[0], "name": role[1]} for role in roles],
            safe=False,
            status=200
        )

    @admin_required
    def put(self, request, role_id=None):
        """
        Обновление имени роли по ID.
        """
        if not role_id:
            return JsonResponse({"error": "Role ID is required in URL."}, status=400)

        data = request.data

        # Проверка существования роли
        role_check_query = "SELECT id FROM roles WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(role_check_query, [role_id])
            existing_role = cursor.fetchone()

        if not existing_role:
            return JsonResponse({"error": "Role not found."}, status=404)

        # Проверка на уникальность нового имени
        name_check_query = "SELECT id FROM roles WHERE name = %s AND id != %s"
        with connection.cursor() as cursor:
            cursor.execute(name_check_query, [data['name'], role_id])
            name_conflict = cursor.fetchone()

        if name_conflict:
            return JsonResponse({"error": "Role name already exists."}, status=400)

        # Обновление имени роли
        query = "UPDATE roles SET name = %s WHERE id = %s RETURNING id, name;"
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, [data['name'], role_id])
                updated_role = cursor.fetchone()
            except Exception as e:
                return JsonResponse({"error": "Unable to update role. " + str(e)}, status=400)

        return JsonResponse({"id": updated_role[0], "name": updated_role[1]}, status=200)

    @admin_required
    def delete(self, request, role_id=None):
        """
        Удаление роли по ID.
        """
        if not role_id:
            return JsonResponse({"error": "Role ID is required in URL."}, status=400)

        # Проверка существования роли
        role_check_query = "SELECT id FROM roles WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(role_check_query, [role_id])
            existing_role = cursor.fetchone()

        if not existing_role:
            return JsonResponse({"error": "Role not found."}, status=404)

        # Удаление роли
        query = "DELETE FROM roles WHERE id = %s;"
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, [role_id])
            except Exception as e:
                return JsonResponse({"error": "Unable to delete role. " + str(e)}, status=400)

        return JsonResponse({"detail": "Role deleted successfully."}, status=200)


class LevelAPIView(APIView):

    @admin_required
    def post(self, request):
        """
        Создание нового уровня.
        """
        data = request.data

        # Проверка на существующее имя уровня
        name_query = "SELECT id FROM levels WHERE name = %s"
        with connection.cursor() as cursor:
            cursor.execute(name_query, [data['name']])
            existing_name = cursor.fetchone()

        if existing_name:
            return JsonResponse({"error": "Level name already exists."}, status=400)

        # Вставка нового уровня
        query = "INSERT INTO levels (name) VALUES (%s) RETURNING id, name;"
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, [data['name']])
                level = cursor.fetchone()
            except Exception as e:
                return JsonResponse({"error": "Unable to create level. " + str(e)}, status=400)

        return JsonResponse({"id": level[0], "name": level[1]}, status=201)

    @admin_required
    def get(self, request):
        """
        Получение списка всех уровней.
        """
        query = "SELECT id, name FROM levels ORDER BY id;"
        with connection.cursor() as cursor:
            cursor.execute(query)
            levels = cursor.fetchall()

        return JsonResponse(
            [{"id": level[0], "name": level[1]} for level in levels],
            safe=False,
            status=200
        )

    @admin_required
    def put(self, request, level_id=None):
        """
        Обновление имени уровня по ID.
        """
        if not level_id:
            return JsonResponse({"error": "Level ID is required in URL."}, status=400)

        data = request.data

        # Проверка существования уровня
        level_check_query = "SELECT id FROM levels WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(level_check_query, [level_id])
            existing_level = cursor.fetchone()

        if not existing_level:
            return JsonResponse({"error": "Level not found."}, status=404)

        # Проверка на уникальность нового имени
        name_check_query = "SELECT id FROM levels WHERE name = %s AND id != %s"
        with connection.cursor() as cursor:
            cursor.execute(name_check_query, [data['name'], level_id])
            name_conflict = cursor.fetchone()

        if name_conflict:
            return JsonResponse({"error": "Level name already exists."}, status=400)

        # Обновление имени уровня
        query = "UPDATE levels SET name = %s WHERE id = %s RETURNING id, name;"
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, [data['name'], level_id])
                updated_level = cursor.fetchone()
            except Exception as e:
                return JsonResponse({"error": "Unable to update level. " + str(e)}, status=400)

        return JsonResponse({"id": updated_level[0], "name": updated_level[1]}, status=200)

    @admin_required
    def delete(self, request, level_id=None):
        """
        Удаление уровня по ID.
        """
        if not level_id:
            return JsonResponse({"error": "Level ID is required in URL."}, status=400)

        # Проверка существования уровня
        level_check_query = "SELECT id FROM levels WHERE id = %s"
        with connection.cursor() as cursor:
            cursor.execute(level_check_query, [level_id])
            existing_level = cursor.fetchone()

        if not existing_level:
            return JsonResponse({"error": "Level not found."}, status=404)

        # Удаление уровня
        query = "DELETE FROM levels WHERE id = %s;"
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, [level_id])
            except Exception as e:
                return JsonResponse({"error": "Unable to delete level. " + str(e)}, status=400)

        return JsonResponse({"detail": "Level deleted successfully."}, status=200)
    

class CategoryMaterialAPIView(APIView):
    def post(self, request):
        """
        Создание новой категории материалов.
        """
        data = request.data

        query = "INSERT INTO categorymaterials (name) VALUES (%s) RETURNING id, name;"
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, [data['name']])
                category = cursor.fetchone()
            except Exception as e:
                return JsonResponse({"error": "Unable to create category. " + str(e)}, status=400)

        return JsonResponse({"id": category[0], "name": category[1]}, status=201)

