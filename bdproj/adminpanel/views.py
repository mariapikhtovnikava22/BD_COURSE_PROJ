from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from auth_users.utils.hash_password import hash_password
from django.http import JsonResponse
from .serializers import UserSerializer, RoleSerializer, LevelSerializer
from .utils.admin_required import admin_required
from .utils.base_api import BaseAPIView
from .utils.base_sql_handler import BaseSQLHandler

class AdminUserAPIView(BaseAPIView):

    @admin_required
    def get(self, request, user_id=None):
        """
        Получение списка всех пользователей или информации о конкретном пользователе.
        """
        if user_id:
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
            user = BaseSQLHandler.execute_query(query, [user_id], fetchone=True)
            if not user:
                return JsonResponse({"detail": "User not found."}, status=404)

            serializer = UserSerializer({
                "id": user[0],
                "fio": user[1],
                "email": user[2],
                "is_active": user[3],
                "role": user[4],
                "level": user[5],
                "entrance_test": user[6],
            })
            return JsonResponse(serializer.data, status=200)

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
        users = BaseSQLHandler.execute_query(query, fetchall=True)

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
        return JsonResponse(users_data, safe=False, status=200)

    @admin_required
    def post(self, request):
        """
        Создание нового пользователя.
        """
        data = request.data
        hashed_password = hash_password(data['password'])

        if not self.validate_unique_field("users", "email", data["email"]):
            return JsonResponse({"error": "Email already exists."}, status=400)

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
        try:
            user = BaseSQLHandler.execute_query(query, [
                data['fio'], data['email'], hashed_password,
                data['role'], data.get('level'),
                data.get('is_active', True), data.get('entrance_test', False)
            ], fetchone=True)
        except Exception as e:
            return JsonResponse({"error": f"Unable to create user: {e}"}, status=400)

        serializer = UserSerializer({
            "id": user[0],
            "fio": user[1],
            "email": user[2],
            "is_active": user[3],
            "role": user[4],
            "level": user[5],
            "entrance_test": user[6],
        })
        return JsonResponse(serializer.data, status=201)

    @admin_required
    def put(self, request, user_id=None):
        """
        Обновление информации о пользователе.
        """
        if not user_id:
            return JsonResponse({"detail": "User ID is required in URL."}, status=400)

        user = self.get_object_by_id("users", user_id)
        if not user:
            return JsonResponse({"detail": "User with the given ID does not exist."}, status=404)

        data = request.data

        # Проверка уникальности email (если email передан)
        email = data.get('email')
        if email and not self.validate_unique_field("users", "email", email, exclude_id=user_id):
            return JsonResponse({"error": "Email already exists."}, status=400)

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

        if not update_fields:
            return JsonResponse({"detail": "No fields to update."}, status=400)

        query = f"""
        UPDATE users
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, fio, email, is_active, 
                (SELECT name FROM roles WHERE id = role_id), 
                (SELECT name FROM levels WHERE id = level_id), 
                entrance_test;
        """
        values.append(user_id)

        try:
            user = BaseSQLHandler.execute_query(query, values, fetchone=True)
        except Exception as e:
            return JsonResponse({"error": f"Unable to update user: {e}"}, status=400)

        serializer = UserSerializer({
            "id": user[0],
            "fio": user[1],
            "email": user[2],
            "is_active": user[3],
            "role": user[4],
            "level": user[5],
            "entrance_test": user[6],
        })
        return JsonResponse(serializer.data, status=200)

    @admin_required
    def delete(self, request, user_id=None):
        """
        Удаление пользователя.
        """
        if not user_id:
            return JsonResponse({"detail": "User ID is required in URL."}, status=400)

        user = self.get_object_by_id("users", user_id)
        if not user:
            return JsonResponse({"detail": "User with the given ID does not exist."}, status=404)

        query = "DELETE FROM users WHERE id = %s"
        try:
            BaseSQLHandler.execute_query(query, [user_id])
        except Exception as e:
            return JsonResponse({"error": f"Unable to delete user: {e}"}, status=400)

        return JsonResponse({"detail": "User deleted successfully."}, status=200)


class RoleAPIView(BaseAPIView):

    @admin_required
    def post(self, request):
        """
        Создание новой роли.
        """
        data = request.data
        if not self.validate_unique_field("roles", "name", data['name']):
            return JsonResponse({"error": "Role name already exists."}, status=400)

        query = "INSERT INTO roles (name) VALUES (%s) RETURNING id, name;"
        try:
            role = BaseSQLHandler.execute_query(query, [data['name']], fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to create role", e)

        serializer = RoleSerializer({"id": role[0], "name": role[1]})
        return JsonResponse(serializer.data, status=201)

    @admin_required
    def get(self, request, role_id=None):
        """
        Получение списка всех ролей или информации о конкретной роли.
        """
        if role_id:
            query = "SELECT id, name FROM roles WHERE id = %s;"
            role = BaseSQLHandler.execute_query(query, [role_id], fetchone=True)

            if not role:
                return JsonResponse({"error": "Role not found."}, status=404)

            serializer = RoleSerializer({"id": role[0], "name": role[1]})
            return JsonResponse(serializer.data, status=200)

        query = "SELECT id, name FROM roles ORDER BY id;"
        roles = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [{"id": role[0], "name": role[1]} for role in roles]
        return JsonResponse(response, safe=False, status=200)

    @admin_required
    def put(self, request, role_id=None):
        """
        Обновление имени роли по ID.
        """
        if not role_id:
            return JsonResponse({"error": "Role ID is required in URL."}, status=400)

        if not self.get_object_by_id("roles", role_id):
            return JsonResponse({"error": "Role not found."}, status=404)

        data = request.data
        if not self.validate_unique_field("roles", "name", data['name'], exclude_id=role_id):
            return JsonResponse({"error": "Role name already exists."}, status=400)

        query = "UPDATE roles SET name = %s WHERE id = %s RETURNING id, name;"
        try:
            updated_role = BaseSQLHandler.execute_query(query, [data['name'], role_id], fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to update role", e)

        serializer = RoleSerializer({"id": updated_role[0], "name": updated_role[1]})
        return JsonResponse(serializer.data, status=200)

    @admin_required
    def delete(self, request, role_id=None):
        """
        Удаление роли по ID.
        """
        if not role_id:
            return JsonResponse({"error": "Role ID is required in URL."}, status=400)

        if not self.get_object_by_id("roles", role_id):
            return JsonResponse({"error": "Role not found."}, status=404)

        query = "DELETE FROM roles WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [role_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete role", e)

        return JsonResponse({"detail": "Role deleted successfully."}, status=200)


class LevelAPIView(BaseAPIView):

    @admin_required
    def post(self, request):
        """
        Создание нового уровня.
        """
        data = request.data

        # Проверка на существующее имя уровня
        if not self.validate_unique_field("levels", "name", data['name']):
            return JsonResponse({"error": "Level name already exists."}, status=400)

        # Вставка нового уровня
        query = "INSERT INTO levels (name) VALUES (%s) RETURNING id, name;"
        try:
            level = BaseSQLHandler.execute_query(query, [data['name']], fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to create level", e)

        serializer = LevelSerializer({"id": level[0], "name": level[1]})
        return JsonResponse(serializer.data, status=201)

    @admin_required
    def get(self, request, level_id=None):
        """
        Получение списка всех уровней или информации о конкретном уровне.
        """
        if level_id:
            query = "SELECT id, name FROM levels WHERE id = %s;"
            level = BaseSQLHandler.execute_query(query, [level_id], fetchone=True)

            if not level:
                return JsonResponse({"error": "Level not found."}, status=404)

            serializer = LevelSerializer({"id": level[0], "name": level[1]})
            return JsonResponse(serializer.data, status=200)

        query = "SELECT id, name FROM levels ORDER BY id;"
        levels = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [{"id": level[0], "name": level[1]} for level in levels]
        return JsonResponse(response, safe=False, status=200)

    @admin_required
    def put(self, request, level_id=None):
        """
        Обновление имени уровня по ID.
        """
        if not level_id:
            return JsonResponse({"error": "Level ID is required in URL."}, status=400)

        if not self.get_object_by_id("levels", level_id):
            return JsonResponse({"error": "Level not found."}, status=404)

        data = request.data

        # Проверка на уникальность нового имени
        if not self.validate_unique_field("levels", "name", data['name'], exclude_id=level_id):
            return JsonResponse({"error": "Level name already exists."}, status=400)

        # Обновление имени уровня
        query = "UPDATE levels SET name = %s WHERE id = %s RETURNING id, name;"
        try:
            updated_level = BaseSQLHandler.execute_query(query, [data['name'], level_id], fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to update level", e)

        serializer = LevelSerializer({"id": updated_level[0], "name": updated_level[1]})
        return JsonResponse(serializer.data, status=200)

    @admin_required
    def delete(self, request, level_id=None):
        """
        Удаление уровня по ID.
        """
        if not level_id:
            return JsonResponse({"error": "Level ID is required in URL."}, status=400)

        if not self.get_object_by_id("levels", level_id):
            return JsonResponse({"error": "Level not found."}, status=404)

        query = "DELETE FROM levels WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [level_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete level", e)

        return JsonResponse({"detail": "Level deleted successfully."}, status=200)


class CategoryMaterialAPIView(BaseAPIView):

    @admin_required
    def post(self, request):
        """
        Создание новой категории материалов.
        """
        data = request.data

        # Проверка на существующее имя категории
        if not self.validate_unique_field("categorymaterials", "name", data['name']):
            return JsonResponse({"error": "Category name already exists."}, status=400)

        # Вставка новой категории
        query = "INSERT INTO categorymaterials (name) VALUES (%s) RETURNING id, name;"
        try:
            category = BaseSQLHandler.execute_query(query, [data['name']], fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to create category", e)

        return JsonResponse({"id": category[0], "name": category[1]}, status=201)


    @admin_required
    def get(self, request, category_id=None):
        """
        Получение списка всех категорий материалов или информации о конкретной категории.
        """
        if category_id:
            query = "SELECT id, name FROM categorymaterials WHERE id = %s;"
            category = BaseSQLHandler.execute_query(query, [category_id], fetchone=True)

            if not category:
                return JsonResponse({"error": "Category not found."}, status=404)

            return JsonResponse({"id": category[0], "name": category[1]}, status=200)

        query = "SELECT id, name FROM categorymaterials ORDER BY id;"
        categories = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [{"id": category[0], "name": category[1]} for category in categories]
        return JsonResponse(response, safe=False, status=200)


    @admin_required
    def put(self, request, category_id=None):
        """
        Обновление имени категории по ID.
        """
        if not category_id:
            return JsonResponse({"error": "Category ID is required in URL."}, status=400)

        if not self.get_object_by_id("categorymaterials", category_id):
            return JsonResponse({"error": "Category not found."}, status=404)

        data = request.data

        # Проверка на уникальность нового имени
        if not self.validate_unique_field("categorymaterials", "name", data['name'], exclude_id=category_id):
            return JsonResponse({"error": "Category name already exists."}, status=400)

        # Обновление имени категории
        query = "UPDATE categorymaterials SET name = %s WHERE id = %s RETURNING id, name;"
        try:
            updated_category = BaseSQLHandler.execute_query(query, [data['name'], category_id], fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to update category", e)

        return JsonResponse({"id": updated_category[0], "name": updated_category[1]}, status=200)

    @admin_required
    def delete(self, request, category_id=None):
        """
        Удаление категории по ID.
        """
        if not category_id:
            return JsonResponse({"error": "Category ID is required in URL."}, status=400)

        if not self.get_object_by_id("categorymaterials", category_id):
            return JsonResponse({"error": "Category not found."}, status=404)

        query = "DELETE FROM categorymaterials WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [category_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete category", e)

        return JsonResponse({"detail": "Category deleted successfully."}, status=200)
    

class ModuleAPIView(BaseAPIView):
    @admin_required
    def post(self, request):
        """
        Создание нового модуля.
        """
        data = request.data

        # Проверка уникальности имени модуля
        if not self.validate_unique_field("modules", "name", data['name']):
            return JsonResponse({"error": "Module name already exists."}, status=400)

        # Вставка нового модуля
        query = """
        INSERT INTO modules (name, description, level_id)
        VALUES (%s, %s, %s)
        RETURNING id, name, description, level_id;
        """
        try:
            module = BaseSQLHandler.execute_query(query, [
                data['name'],
                data.get('description'),
                data['level_id']
            ], fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to create module", e)

        return JsonResponse({
            "id": module[0],
            "name": module[1],
            "description": module[2],
            "level_id": module[3]
        }, status=201)

    @admin_required
    def get(self, request, module_id=None):
        """
        Получение списка всех модулей или информации о конкретном модуле.
        """
        if module_id:
            query = """
            SELECT m.id, m.name, m.description, l.name AS level_name  
            FROM modules AS m
            LEFT JOIN levels AS l ON m.level_id = l.id
            WHERE m.id = %s;
            """
            module = BaseSQLHandler.execute_query(query, [module_id], fetchone=True)

            if not module:
                return JsonResponse({"error": "Module not found."}, status=404)

            return JsonResponse({
                "id": module[0],
                "name": module[1],
                "description": module[2],
                "level_name": module[3]
            }, status=200)

        query = """
        SELECT m.id, m.name, m.description, l.name AS level_name  
        FROM modules AS m
        LEFT JOIN levels AS l ON m.level_id = l.id
        ORDER BY m.id;
        """
        modules = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [
            {"id": module[0], "name": module[1], "description": module[2], "level_name": module[3]}
            for module in modules
        ]
        return JsonResponse(response, safe=False, status=200)

    @admin_required
    def put(self, request, module_id=None):
        """
        Обновление информации о модуле по ID.
        """
        if not module_id:
            return JsonResponse({"error": "Module ID is required in URL."}, status=400)

        if not self.get_object_by_id("modules", module_id):
            return JsonResponse({"error": "Module not found."}, status=404)

        data = request.data

        # Проверка уникальности нового имени
        if 'name' in data and not self.validate_unique_field("modules", "name", data['name'], exclude_id=module_id):
            return JsonResponse({"error": "Module name already exists."}, status=400)

        # Построение запроса для обновления
        update_fields = []
        values = []

        if 'name' in data:
            update_fields.append("name = %s")
            values.append(data['name'])
        if 'description' in data:
            update_fields.append("description = %s")
            values.append(data['description'])
        if 'level_id' in data:
            update_fields.append("level_id = %s")
            values.append(data['level_id'])

        if not update_fields:
            return JsonResponse({"error": "No fields to update."}, status=400)

        query = f"UPDATE modules SET {', '.join(update_fields)} WHERE id = %s RETURNING id, name, description, level_id;"
        values.append(module_id)

        try:
            updated_module = BaseSQLHandler.execute_query(query, values, fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to update module", e)

        return JsonResponse({
            "id": updated_module[0],
            "name": updated_module[1],
            "description": updated_module[2],
            "level_id": updated_module[3]
        }, status=200)

    @admin_required
    def delete(self, request, module_id=None):
        """
        Удаление модуля по ID.
        """
        if not module_id:
            return JsonResponse({"error": "Module ID is required in URL."}, status=400)

        if not self.get_object_by_id("modules", module_id):
            return JsonResponse({"error": "Module not found."}, status=404)

        query = "DELETE FROM modules WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [module_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete module", e)

        return JsonResponse({"detail": "Module deleted successfully."}, status=200)


class TopicAPIView(BaseAPIView):
    @admin_required
    def post(self, request):
        """
        Создание новой темы.
        """
        data = request.data

        # Проверка уникальности имени темы
        if not self.validate_unique_field("topics", "name", data['name']):
            return JsonResponse({"error": "Topic name already exists."}, status=400)

        # Вставка новой темы
        query = """
        INSERT INTO topics (name, description, module_id)
        VALUES (%s, %s, %s)
        RETURNING id, name, description, module_id;
        """
        try:
            topic = BaseSQLHandler.execute_query(query, [
                data['name'],
                data.get('description'),
                data['module_id']
            ], fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to create topic", e)

        return JsonResponse({
            "id": topic[0],
            "name": topic[1],
            "description": topic[2],
            "module_id": topic[3]
        }, status=201)

    @admin_required
    def get(self, request, topic_id=None):
        """
        Получение списка всех тем или информации о конкретной теме.
        """
        if topic_id:
            query = """
            SELECT t.id, t.name, t.description, m.name AS module_name 
            FROM topics AS t
            LEFT JOIN modules AS m ON t.module_id = m.id
            WHERE t.id = %s;
            """
            topic = BaseSQLHandler.execute_query(query, [topic_id], fetchone=True)

            if not topic:
                return JsonResponse({"error": "Topic not found."}, status=404)

            return JsonResponse({
                "id": topic[0],
                "name": topic[1],
                "description": topic[2],
                "module_name": topic[3]
            }, status=200)

        query = """
        SELECT t.id, t.name, t.description, m.name AS module_name 
        FROM topics AS t
        LEFT JOIN modules AS m ON t.module_id = m.id
        ORDER BY t.id;
        """
        topics = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [
            {"id": topic[0], "name": topic[1], "description": topic[2], "module_name": topic[3]}
            for topic in topics
        ]
        return JsonResponse(response, safe=False, status=200)


    @admin_required
    def put(self, request, topic_id=None):
        """
        Обновление информации о теме по ID.
        """
        if not topic_id:
            return JsonResponse({"error": "Topic ID is required in URL."}, status=400)

        if not self.get_object_by_id("topics", topic_id):
            return JsonResponse({"error": "Topic not found."}, status=404)

        data = request.data

        # Проверка уникальности нового имени
        if 'name' in data and not self.validate_unique_field("topics", "name", data['name'], exclude_id=topic_id):
            return JsonResponse({"error": "Topic name already exists."}, status=400)

        # Построение запроса для обновления
        update_fields = []
        values = []

        if 'name' in data:
            update_fields.append("name = %s")
            values.append(data['name'])
        if 'description' in data:
            update_fields.append("description = %s")
            values.append(data['description'])
        if 'module_id' in data:
            update_fields.append("module_id = %s")
            values.append(data['module_id'])

        if not update_fields:
            return JsonResponse({"error": "No fields to update."}, status=400)
        
        query = f"UPDATE topics SET {', '.join(update_fields)} WHERE id = %s RETURNING id, name, description, module_id;"
        values.append(topic_id)

        try:
            updated_topic = BaseSQLHandler.execute_query(query, values, fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to update topic", e)

        return JsonResponse({
            "id": updated_topic[0],
            "name": updated_topic[1],
            "description": updated_topic[2],
            "module_id": updated_topic[3]
        }, status=200)

    @admin_required
    def delete(self, request, topic_id=None):
        """
        Удаление темы по ID.
        """
        if not topic_id:
            return JsonResponse({"error": "Topic ID is required in URL."}, status=400)

        if not self.get_object_by_id("topics", topic_id):
            return JsonResponse({"error": "Topic not found."}, status=404)

        query = "DELETE FROM topics WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [topic_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete topic", e)

        return JsonResponse({"detail": "Topic deleted successfully."}, status=200)

