from django.db import connection
import os
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from auth_users.utils.hash_password import hash_password
from django.core.files.storage import FileSystemStorage
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
                u.role_id, 
                u.level_id, 
                u.entrance_test
            FROM users u
            WHERE u.id = %s
            """
            user = BaseSQLHandler.execute_query(query, [user_id], fetchone=True)
            if not user:
                return JsonResponse({"detail": "User not found."}, status=404)

            serializer = UserSerializer(
                {
                    "id": user[0],
                    "fio": user[1],
                    "email": user[2],
                    "is_active": user[3],
                    "role_id": user[4],
                    "level_id": user[5],
                    "entrance_test": user[6],
                }
            )
            return JsonResponse(serializer.data, status=200)

        query = """
        SELECT 
            u.id, u.fio, u.email, u.is_active, 
            u.role_id, 
            u.level_id, 
            u.entrance_test
        FROM users u
        WHERE u.role_id != (SELECT id FROM roles WHERE name = 'admin'); 
        """
        users = BaseSQLHandler.execute_query(query, fetchall=True)

        users_data = [
            {
                "id": user[0],
                "fio": user[1],
                "email": user[2],
                "is_active": user[3],
                "role_id": user[4],
                "level_id": user[5],
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
        hashed_password = hash_password(data["password"])

        if not self.validate_unique_field("users", "email", data["email"]):
            return JsonResponse({"error": "Email already exists."}, status=400)

        query = """
        INSERT INTO users (fio, email, password, role_id, level_id, is_active, entrance_test)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, fio, email, is_active, 
                  role_id, 
                  level_id, 
                  entrance_test;
        """
        try:
            user = BaseSQLHandler.execute_query(
                query,
                [
                    data["fio"],
                    data["email"],
                    hashed_password,
                    data["role_id"],
                    data.get("level_id"),
                    data.get("is_active", True),
                    data.get("entrance_test", False),
                ],
                fetchone=True,
            )
        except Exception as e:
            return JsonResponse({"error": f"Unable to create user: {e}"}, status=400)

        serializer = UserSerializer(
            {
                "id": user[0],
                "fio": user[1],
                "email": user[2],
                "is_active": user[3],
                "role_id": user[4],
                "level_id": user[5],
                "entrance_test": user[6],
            }
        )
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
            return JsonResponse(
                {"detail": "User with the given ID does not exist."}, status=404
            )

        data = request.data

        # Проверка уникальности email (если email передан)
        email = data.get("email")
        if email and not self.validate_unique_field(
            "users", "email", email, exclude_id=user_id
        ):
            return JsonResponse({"error": "Email already exists."}, status=400)

        update_fields = []
        values = []

        if "fio" in data:
            update_fields.append("fio = %s")
            values.append(data["fio"])

        if "email" in data:
            update_fields.append("email = %s")
            values.append(data["email"])

        if "role_id" in data:
            update_fields.append("role_id = %s")
            values.append(data["role_id"])

        if "level_id" in data:
            update_fields.append("level_id = %s")
            values.append(data["level_id"])

        if "is_active" in data:
            update_fields.append("is_active = %s")
            values.append(data["is_active"])

        if "entrance_test" in data:
            update_fields.append("entrance_test = %s")
            values.append(data["entrance_test"])

        if not update_fields:
            return JsonResponse({"detail": "No fields to update."}, status=400)

        query = f"""
        UPDATE users
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, fio, email, is_active, 
                role_id, 
                level_id, 
                entrance_test;
        """
        values.append(user_id)

        try:
            user = BaseSQLHandler.execute_query(query, values, fetchone=True)
        except Exception as e:
            return JsonResponse({"error": f"Unable to update user: {e}"}, status=400)

        serializer = UserSerializer(
            {
                "id": user[0],
                "fio": user[1],
                "email": user[2],
                "is_active": user[3],
                "role_id": user[4],
                "level_id": user[5],
                "entrance_test": user[6],
            }
        )
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
            return JsonResponse(
                {"detail": "User with the given ID does not exist."}, status=404
            )

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
        if not self.validate_unique_field("roles", "name", data["name"]):
            return JsonResponse({"error": "Role name already exists."}, status=400)

        query = "INSERT INTO roles (name) VALUES (%s) RETURNING id, name;"
        try:
            role = BaseSQLHandler.execute_query(query, [data["name"]], fetchone=True)
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
        if not self.validate_unique_field(
            "roles", "name", data["name"], exclude_id=role_id
        ):
            return JsonResponse({"error": "Role name already exists."}, status=400)

        query = "UPDATE roles SET name = %s WHERE id = %s RETURNING id, name;"
        try:
            updated_role = BaseSQLHandler.execute_query(
                query, [data["name"], role_id], fetchone=True
            )
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
        if not self.validate_unique_field("levels", "name", data["name"]):
            return JsonResponse({"error": "Level name already exists."}, status=400)

        # Вставка нового уровня
        query = "INSERT INTO levels (name) VALUES (%s) RETURNING id, name;"
        try:
            level = BaseSQLHandler.execute_query(query, [data["name"]], fetchone=True)
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
        if not self.validate_unique_field(
            "levels", "name", data["name"], exclude_id=level_id
        ):
            return JsonResponse({"error": "Level name already exists."}, status=400)

        # Обновление имени уровня
        query = "UPDATE levels SET name = %s WHERE id = %s RETURNING id, name;"
        try:
            updated_level = BaseSQLHandler.execute_query(
                query, [data["name"], level_id], fetchone=True
            )
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
        if not self.validate_unique_field("categorymaterials", "name", data["name"]):
            return JsonResponse({"error": "Category name already exists."}, status=400)

        # Вставка новой категории
        query = "INSERT INTO categorymaterials (name) VALUES (%s) RETURNING id, name;"
        try:
            category = BaseSQLHandler.execute_query(
                query, [data["name"]], fetchone=True
            )
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
            return JsonResponse(
                {"error": "Category ID is required in URL."}, status=400
            )

        if not self.get_object_by_id("categorymaterials", category_id):
            return JsonResponse({"error": "Category not found."}, status=404)

        data = request.data

        # Проверка на уникальность нового имени
        if not self.validate_unique_field(
            "categorymaterials", "name", data["name"], exclude_id=category_id
        ):
            return JsonResponse({"error": "Category name already exists."}, status=400)

        # Обновление имени категории
        query = (
            "UPDATE categorymaterials SET name = %s WHERE id = %s RETURNING id, name;"
        )
        try:
            updated_category = BaseSQLHandler.execute_query(
                query, [data["name"], category_id], fetchone=True
            )
        except Exception as e:
            return self.handle_database_error("Unable to update category", e)

        return JsonResponse(
            {"id": updated_category[0], "name": updated_category[1]}, status=200
        )

    @admin_required
    def delete(self, request, category_id=None):
        """
        Удаление категории по ID.
        """
        if not category_id:
            return JsonResponse(
                {"error": "Category ID is required in URL."}, status=400
            )

        if not self.get_object_by_id("categorymaterials", category_id):
            return JsonResponse({"error": "Category not found."}, status=404)

        query = "DELETE FROM categorymaterials WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [category_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete category", e)

        return JsonResponse({"detail": "Category deleted successfully."}, status=200)


class BulkModuleAPIView(BaseAPIView):
    @admin_required
    def post(self, request):
        """
        Массовое добавление модулей с темами из JSON-файла.
        """
        data = request.data  # Предполагаем, что данные приходят в формате JSON.

        if not isinstance(data, list):
            return JsonResponse(
                {"error": "Data should be a list of modules with topics."}, status=400
            )

        created_modules = []
        try:
            for module in data:
                module_name = module.get("name")
                module_description = module.get("description", "")
                module_level_id = module.get("level_id")

                # Проверка обязательных полей
                if not module_name or not module_level_id:
                    return JsonResponse(
                        {"error": f"Module name and level_id are required: {module}"},
                        status=400,
                    )

                # Вставка модуля
                module_query = """
                INSERT INTO modules (name, description, level_id)
                VALUES (%s, %s, %s)
                RETURNING id, name, description, level_id;
                """
                created_module = BaseSQLHandler.execute_query(
                    module_query,
                    [module_name, module_description, module_level_id],
                    fetchone=True,
                )

                module_id = created_module[0]
                created_modules.append(
                    {
                        "id": created_module[0],
                        "name": created_module[1],
                        "description": created_module[2],
                        "level_id": created_module[3],
                    }
                )

                # Добавление тем, если они указаны
                topics = module.get("topics", [])
                for topic in topics:
                    topic_name = topic.get("name")
                    topic_description = topic.get("description", "")

                    # Проверка обязательных полей темы
                    if not topic_name:
                        return JsonResponse(
                            {"error": f"Topic name is required: {topic}"}, status=400
                        )

                    topic_query = """
                    INSERT INTO topics (name, description, module_id)
                    VALUES (%s, %s, %s);
                    """
                    BaseSQLHandler.execute_query(
                        topic_query, [topic_name, topic_description, module_id]
                    )

        except Exception as e:
            return self.handle_database_error(
                "Failed to bulk add modules and topics", e
            )

        return JsonResponse(
            {
                "detail": "Modules and topics added successfully.",
                "modules": created_modules,
            },
            status=201,
        )


class ModuleAPIView(BaseAPIView):
    @admin_required
    def post(self, request):
        """
        Создание нового модуля.
        """
        data = request.data

        # Проверка уникальности имени модуля
        if not self.validate_unique_field("modules", "name", data["name"]):
            return JsonResponse({"error": "Module name already exists."}, status=400)

        # Вставка нового модуля
        query = """
        INSERT INTO modules (name, description, level_id)
        VALUES (%s, %s, %s)
        RETURNING id, name, description, level_id;
        """
        try:
            module = BaseSQLHandler.execute_query(
                query,
                [data["name"], data.get("description"), data["level_id"]],
                fetchone=True,
            )
        except Exception as e:
            return self.handle_database_error("Unable to create module", e)

        return JsonResponse(
            {
                "id": module[0],
                "name": module[1],
                "description": module[2],
                "level_id": module[3],
            },
            status=201,
        )

    @admin_required
    def get(self, request, module_id=None):
        """
        Получение списка всех модулей или информации о конкретном модуле.
        """
        if module_id:
            query = """
            SELECT m.id, m.name, m.description, m.level_id  
            FROM modules AS m
            WHERE m.id = %s;
            """
            module = BaseSQLHandler.execute_query(query, [module_id], fetchone=True)

            if not module:
                return JsonResponse({"error": "Module not found."}, status=404)

            return JsonResponse(
                {
                    "id": module[0],
                    "name": module[1],
                    "description": module[2],
                    "level_id": module[3],  # Возвращаем level_id
                },
                status=200,
            )

        query = """
        SELECT m.id, m.name, m.description, m.level_id  
        FROM modules AS m
        ORDER BY m.id;
        """
        modules = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [
            {
                "id": module[0],
                "name": module[1],
                "description": module[2],
                "level_id": module[3],  # Возвращаем level_id
            }
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
        if "name" in data and not self.validate_unique_field(
            "modules", "name", data["name"], exclude_id=module_id
        ):
            return JsonResponse({"error": "Module name already exists."}, status=400)

        # Построение запроса для обновления
        update_fields = []
        values = []

        if "name" in data:
            update_fields.append("name = %s")
            values.append(data["name"])
        if "description" in data:
            update_fields.append("description = %s")
            values.append(data["description"])
        if "level_id" in data:
            update_fields.append("level_id = %s")
            values.append(data["level_id"])

        if not update_fields:
            return JsonResponse({"error": "No fields to update."}, status=400)

        query = f"UPDATE modules SET {', '.join(update_fields)} WHERE id = %s RETURNING id, name, description, level_id;"
        values.append(module_id)

        try:
            updated_module = BaseSQLHandler.execute_query(query, values, fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to update module", e)

        return JsonResponse(
            {
                "id": updated_module[0],
                "name": updated_module[1],
                "description": updated_module[2],
                "level_id": updated_module[3],
            },
            status=200,
        )

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
        if not self.validate_unique_field("topics", "name", data["name"]):
            return JsonResponse({"error": "Topic name already exists."}, status=400)

        # Вставка новой темы
        query = """
        INSERT INTO topics (name, description, module_id)
        VALUES (%s, %s, %s)
        RETURNING id, name, description, module_id;
        """
        try:
            topic = BaseSQLHandler.execute_query(
                query,
                [data["name"], data.get("description"), data["module_id"]],
                fetchone=True,
            )
        except Exception as e:
            return self.handle_database_error("Unable to create topic", e)

        return JsonResponse(
            {
                "id": topic[0],
                "name": topic[1],
                "description": topic[2],
                "module_id": topic[3],
            },
            status=201,
        )

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

            return JsonResponse(
                {
                    "id": topic[0],
                    "name": topic[1],
                    "description": topic[2],
                    "module_name": topic[3],
                },
                status=200,
            )

        query = """
        SELECT t.id, t.name, t.description, m.name AS module_name 
        FROM topics AS t
        LEFT JOIN modules AS m ON t.module_id = m.id
        ORDER BY t.id;
        """
        topics = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [
            {
                "id": topic[0],
                "name": topic[1],
                "description": topic[2],
                "module_name": topic[3],
            }
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
        if "name" in data and not self.validate_unique_field(
            "topics", "name", data["name"], exclude_id=topic_id
        ):
            return JsonResponse({"error": "Topic name already exists."}, status=400)

        # Построение запроса для обновления
        update_fields = []
        values = []

        if "name" in data:
            update_fields.append("name = %s")
            values.append(data["name"])
        if "description" in data:
            update_fields.append("description = %s")
            values.append(data["description"])
        if "module_id" in data:
            update_fields.append("module_id = %s")
            values.append(data["module_id"])

        if not update_fields:
            return JsonResponse({"error": "No fields to update."}, status=400)

        query = f"UPDATE topics SET {', '.join(update_fields)} WHERE id = %s RETURNING id, name, description, module_id;"
        values.append(topic_id)

        try:
            updated_topic = BaseSQLHandler.execute_query(query, values, fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to update topic", e)

        return JsonResponse(
            {
                "id": updated_topic[0],
                "name": updated_topic[1],
                "description": updated_topic[2],
                "module_id": updated_topic[3],
            },
            status=200,
        )

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


class TestAPIView(BaseAPIView):
    @admin_required
    def post(self, request):
        """
        Создание нового теста.
        """
        data = request.data

        module_id = data.get("module_id", None)

        # Проверка, существует ли уже тест с таким module_id
        if module_id:
            existing_test_query = """
            SELECT id FROM tests WHERE module_id = %s;
            """
            existing_test = BaseSQLHandler.execute_query(existing_test_query, [data["module_id"]], fetchone=True)
            if existing_test:
                return JsonResponse({"error": f"Test with module_id {data['module_id']} already exists."}, status=400)

        query = """
        INSERT INTO tests (name, module_id)
        VALUES (%s, %s)
        RETURNING id, name, module_id;
        """
        try:
            test = BaseSQLHandler.execute_query(
                query, [data["name"], data.get("module_id")], fetchone=True
            )
        except Exception as e:
            return self.handle_database_error("Unable to create test", e)

        return JsonResponse(
            {"id": test[0], "name": test[1], "module_id": test[2]}, status=201
        )
    
    @admin_required
    def get(self, request, test_id=None):
        """
        Получение списка всех тестов или информации о конкретном тесте.
        """
        if test_id:
            query = """
            SELECT t.id, t.name, t.module_id
            FROM tests AS t
            WHERE t.id = %s;
            """
            test = BaseSQLHandler.execute_query(query, [test_id], fetchone=True)
            if not test:
                return JsonResponse({"error": "Test not found."}, status=404)

            return JsonResponse(
                {"id": test[0], "name": test[1], "module_id": test[2]}, status=200
            )

        query = """
        SELECT t.id, t.name, t.module_id
        FROM tests AS t;
        """
        tests = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [
            {"id": test[0], "name": test[1], "module_id": test[2]} for test in tests
        ]
        return JsonResponse(response, safe=False, status=200)


    @admin_required
    def put(self, request, test_id=None):
        """
        Обновление информации о тесте по ID.
        """
        if not test_id:
            return JsonResponse({"error": "Test ID is required in URL."}, status=400)

        if not self.get_object_by_id("tests", test_id):
            return JsonResponse({"error": "Test not found."}, status=404)

        data = request.data

        # Проверка, существует ли уже тест с таким module_id (кроме текущего теста)
        existing_test_query = """
        SELECT id FROM tests WHERE module_id = %s AND id != %s;
        """
        existing_test = BaseSQLHandler.execute_query(existing_test_query, [data["module_id"], test_id], fetchone=True)
        if existing_test:
            return JsonResponse({"error": f"Test with module_id {data['module_id']} already exists."}, status=400)

        update_fields = []
        values = []

        if "name" in data:
            update_fields.append("name = %s")
            values.append(data["name"])
        if "module_id" in data:
            update_fields.append("module_id = %s")
            values.append(data["module_id"])

        if not update_fields:
            return JsonResponse({"error": "No fields to update."}, status=400)

        query = f"""
        UPDATE tests
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, name, module_id;
        """
        values.append(test_id)

        try:
            updated_test = BaseSQLHandler.execute_query(query, values, fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to update test", e)

        return JsonResponse(
            {
                "id": updated_test[0],
                "name": updated_test[1],
                "module_id": updated_test[2],
            },
            status=200,
        )

    @admin_required
    def delete(self, request, test_id=None):
        """
        Удаление теста по ID.
        """
        if not test_id:
            return JsonResponse({"error": "Test ID is required in URL."}, status=400)

        if not self.get_object_by_id("tests", test_id):
            return JsonResponse({"error": "Test not found."}, status=404)

        query = "DELETE FROM tests WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [test_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete test", e)

        return JsonResponse({"detail": "Test deleted successfully."}, status=200)


class ModuleTestQuestionsAPIView(BaseAPIView):
    @admin_required
    def post(self, request):
        """
        Создание теста с вопросами для указанного модуля.
        """
        data = request.data
        module_id = data.get("module_id")
        test_name = data.get("test_name")
        questions = data.get("questions", [])

        if not module_id or not test_name:
            return JsonResponse({"error": "module_id and test_name are required"}, status=400)

        try:
            # Проверяем, существует ли модуль
            module_check_query = "SELECT id FROM modules WHERE id = %s;"
            module_exists = BaseSQLHandler.execute_query(module_check_query, [module_id], fetchone=True)
            if not module_exists:
                return JsonResponse({"error": "Module not found"}, status=404)

            # Создаём тест
            create_test_query = """
            INSERT INTO tests (name, module_id)
            VALUES (%s, %s)
            RETURNING id, name, module_id;
            """
            created_test = BaseSQLHandler.execute_query(
                create_test_query, [test_name, module_id], fetchone=True
            )
            test_id = created_test[0]

            print("Test create")

            created_questions = []

            # Обрабатываем каждый вопрос
            for question in questions:
                question_text = question.get("question_text")
                topic_id = question.get("topic_id")
                options = question.get("options", [])
                if not question_text:
                    return JsonResponse({"error": "Each question must have 'question_text'"}, status=400)

                # Создаём вопрос
                create_question_query = """
                INSERT INTO questions (name, topic_id, correct_answer_id)
                VALUES (%s, %s, NULL)
                RETURNING id, name;
                """
                created_question = BaseSQLHandler.execute_query(
                    create_question_query,
                    [question_text, topic_id],
                    fetchone=True
                )

                question_id = created_question[0]

                # Связываем вопрос с тестом
                link_test_question_query = """
                INSERT INTO testsquestions (test_id, question_id)
                VALUES (%s, %s);
                """
                BaseSQLHandler.execute_query(link_test_question_query, [test_id, question_id])

                # Создаём варианты ответа
                created_options = []
                for option in options:
                    value = option.get("value")
                    is_correct = option.get("is_correct", False)

                    if not value:
                        continue

                    create_option_query = """
                    INSERT INTO optionss (value)
                    VALUES (%s)
                    RETURNING id, value;
                    """
                    created_option = BaseSQLHandler.execute_query(create_option_query, [value], fetchone=True)

                    option_id = created_option[0]
                    created_options.append({"id": option_id, "value": created_option[1], "is_correct": is_correct})

                    # Связываем вопрос с вариантом
                    create_question_option_query = """
                    INSERT INTO questionoptions (question_id, option_id)
                    VALUES (%s, %s);
                    """
                    BaseSQLHandler.execute_query(create_question_option_query, [question_id, option_id])

                    # Если вариант правильный, обновляем поле correct_answer_id
                    if is_correct:
                        update_correct_answer_query = """
                        UPDATE questions
                        SET correct_answer_id = %s
                        WHERE id = %s;
                        """
                        BaseSQLHandler.execute_query(update_correct_answer_query, [option_id, question_id])

                created_questions.append({
                    "id": question_id,
                    "name": created_question[1],
                    "options": created_options
                })

            return JsonResponse({
                "test": {
                    "id": test_id,
                    "name": created_test[1],
                    "module_id": created_test[2]
                },
                "created_questions": created_questions
            }, status=201)

        except Exception as e:
            return self.handle_database_error("Unable to create test and questions", e)


class UserTestProgressAPIView(BaseAPIView):
    @admin_required
    def post(self, request):
        """
        Создание или обновление прогресса пользователя по тесту.
        """
        data = request.data

        query = """
        INSERT INTO usertestprogress (user_id, test_id, is_passed, attempts, correct_answers)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (user_id, test_id)
        DO UPDATE SET 
            is_passed = EXCLUDED.is_passed,
            attempts = EXCLUDED.attempts,
            correct_answers = EXCLUDED.correct_answers
        RETURNING id, user_id, test_id, is_passed, attempts, correct_answers;
        """
        try:
            progress = BaseSQLHandler.execute_query(
                query,
                [
                    data["user_id"],
                    data["test_id"],
                    data.get("is_passed", False),
                    data.get("attempts", 0),
                    data.get("correct_answers", 0),
                ],
                fetchone=True,
            )
        except Exception as e:
            return self.handle_database_error("Unable to update test progress", e)

        return JsonResponse(
            {
                "id": progress[0],
                "user_id": progress[1],
                "test_id": progress[2],
                "is_passed": progress[3],
                "attempts": progress[4],
                "correct_answers": progress[5],
            },
            status=200,
        )

    @admin_required
    def get(self, request, progress_id=None):
        """
        Получение прогресса пользователя по тесту.
        """
        if progress_id:
            query = """
            SELECT utp.id, u.fio AS user_name, t.name AS test_name, utp.is_passed, utp.attempts, utp.correct_answers
            FROM usertestprogress AS utp
            JOIN users AS u ON utp.user_id = u.id
            JOIN tests AS t ON utp.test_id = t.id
            WHERE utp.id = %s;
            """
            progress = BaseSQLHandler.execute_query(query, [progress_id], fetchone=True)
            if not progress:
                return JsonResponse({"error": "Test progress not found."}, status=404)

            return JsonResponse(
                {
                    "id": progress[0],
                    "user_name": progress[1],
                    "test_name": progress[2],
                    "is_passed": progress[3],
                    "attempts": progress[4],
                    "correct_answers": progress[5],
                },
                status=200,
            )

        query = """
        SELECT utp.id, u.fio AS user_name, t.name AS test_name, utp.is_passed, utp.attempts, utp.correct_answers
        FROM usertestprogress AS utp
        JOIN users AS u ON utp.user_id = u.id
        JOIN tests AS t ON utp.test_id = t.id;
        """
        progresses = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [
            {
                "id": progress[0],
                "user_name": progress[1],
                "test_name": progress[2],
                "is_passed": progress[3],
                "attempts": progress[4],
                "correct_answers": progress[5],
            }
            for progress in progresses
        ]
        return JsonResponse(response, safe=False, status=200)

    @admin_required
    def put(self, request, progress_id=None):
        """
        Обновление прогресса пользователя по тесту.
        """
        if not progress_id:
            return JsonResponse(
                {"error": "Progress ID is required in URL."}, status=400
            )

        if not self.get_object_by_id("usertestprogress", progress_id):
            return JsonResponse({"error": "Progress not found."}, status=404)

        data = request.data
        update_fields = []
        values = []

        if "is_passed" in data:
            update_fields.append("is_passed = %s")
            values.append(data["is_passed"])
        if "attempts" in data:
            update_fields.append("attempts = %s")
            values.append(data["attempts"])
        if "correct_answers" in data:
            update_fields.append("correct_answers = %s")
            values.append(data["correct_answers"])

        if not update_fields:
            return JsonResponse({"error": "No fields to update."}, status=400)

        query = f"""
        UPDATE usertestprogress
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, user_id, test_id, is_passed, attempts, correct_answers;
        """
        values.append(progress_id)

        try:
            updated_progress = BaseSQLHandler.execute_query(
                query, values, fetchone=True
            )
        except Exception as e:
            return self.handle_database_error("Unable to update test progress", e)

        return JsonResponse(
            {
                "id": updated_progress[0],
                "user_id": updated_progress[1],
                "test_id": updated_progress[2],
                "is_passed": updated_progress[3],
                "attempts": updated_progress[4],
                "correct_answers": updated_progress[5],
            },
            status=200,
        )

    @admin_required
    def delete(self, request, progress_id=None):
        """
        Удаление прогресса пользователя по тесту.
        """
        if not progress_id:
            return JsonResponse(
                {"error": "Progress ID is required in URL."}, status=400
            )

        if not self.get_object_by_id("usertestprogress", progress_id):
            return JsonResponse({"error": "Progress not found."}, status=404)

        query = "DELETE FROM usertestprogress WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [progress_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete test progress", e)

        return JsonResponse({"detail": "Progress deleted successfully."}, status=200)


class QuestionsAPIView(BaseAPIView):
    @admin_required
    def post(self, request):
        """
        Создание нового вопроса.
        """
        data = request.data

        query = """
        INSERT INTO questions (name, correct_answer_id, topic_id)
        VALUES (%s, %s, %s)
        RETURNING id, name, correct_answer_id, topic_id;
        """
        try:
            question = BaseSQLHandler.execute_query(
                query,
                [data["name"], data["correct_answer_id"], data["topic_id"]],
                fetchone=True,
            )
        except Exception as e:
            return self.handle_database_error("Unable to create question", e)

        return JsonResponse(
            {
                "id": question[0],
                "name": question[1],
                "correct_answer_id": question[2],
                "topic_id": question[3],
            },
            status=201,
        )

    @admin_required
    def get(self, request, question_id=None):
        """
        Получение списка всех вопросов или информации о конкретном вопросе.
        """
        if question_id:
            query = """
            SELECT q.id, q.name, q.correct_answer_id, t.name AS topic_name
            FROM questions AS q
            LEFT JOIN topics AS t ON q.topic_id = t.id
            WHERE q.id = %s;
            """
            question = BaseSQLHandler.execute_query(query, [question_id], fetchone=True)
            if not question:
                return JsonResponse({"error": "Question not found."}, status=404)

            return JsonResponse(
                {
                    "id": question[0],
                    "name": question[1],
                    "correct_answer_id": question[2],
                    "topic_name": question[3],
                },
                status=200,
            )

        query = """
        SELECT q.id, q.name, q.correct_answer_id, t.name AS topic_name
        FROM questions AS q
        LEFT JOIN topics AS t ON q.topic_id = t.id;
        """
        questions = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [
            {"id": q[0], "name": q[1], "correct_answer_id": q[2], "topic_name": q[3]}
            for q in questions
        ]
        return JsonResponse(response, safe=False, status=200)

    @admin_required
    def put(self, request, question_id=None):
        """
        Обновление информации о вопросе по ID.
        """
        if not question_id:
            return JsonResponse(
                {"error": "Question ID is required in URL."}, status=400
            )

        if not self.get_object_by_id("questions", question_id):
            return JsonResponse({"error": "Question not found."}, status=404)

        data = request.data
        update_fields = []
        values = []

        if "name" in data:
            update_fields.append("name = %s")
            values.append(data["name"])
        if "correct_answer_id" in data:
            update_fields.append("correct_answer_id = %s")
            values.append(data["correct_answer_id"])
        if "topic_id" in data:
            update_fields.append("topic_id = %s")
            values.append(data["topic_id"])

        if not update_fields:
            return JsonResponse({"error": "No fields to update."}, status=400)

        query = f"""
        UPDATE questions
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, name, correct_answer_id, topic_id;
        """
        values.append(question_id)

        try:
            updated_question = BaseSQLHandler.execute_query(
                query, values, fetchone=True
            )
        except Exception as e:
            return self.handle_database_error("Unable to update question", e)

        return JsonResponse(
            {
                "id": updated_question[0],
                "name": updated_question[1],
                "correct_answer_id": updated_question[2],
                "topic_id": updated_question[3],
            },
            status=200,
        )

    @admin_required
    def delete(self, request, question_id=None):
        """
        Удаление вопроса по ID.
        """
        if not question_id:
            return JsonResponse(
                {"error": "Question ID is required in URL."}, status=400
            )

        if not self.get_object_by_id("questions", question_id):
            return JsonResponse({"error": "Question not found."}, status=404)

        query = "DELETE FROM questions WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [question_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete question", e)

        return JsonResponse({"detail": "Question deleted successfully."}, status=200)


class OptionsAPIView(BaseAPIView):
    @admin_required
    def post(self, request):
        """
        Создание нового варианта ответа.
        """
        data = request.data

        query = """
        INSERT INTO optionss (value)
        VALUES (%s)
        RETURNING id, value;
        """
        try:
            option = BaseSQLHandler.execute_query(query, [data["value"]], fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to create option", e)

        return JsonResponse({"id": option[0], "value": option[1]}, status=201)

    @admin_required
    def get(self, request, option_id=None):
        """
        Получение списка всех вариантов или информации о конкретном варианте.
        """
        if option_id:
            query = "SELECT id, value FROM optionss WHERE id = %s;"
            option = BaseSQLHandler.execute_query(query, [option_id], fetchone=True)
            if not option:
                return JsonResponse({"error": "Option not found."}, status=404)

            return JsonResponse({"id": option[0], "value": option[1]}, status=200)

        query = "SELECT id, value FROM optionss;"
        options = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [{"id": o[0], "value": o[1]} for o in options]
        return JsonResponse(response, safe=False, status=200)

    @admin_required
    def put(self, request, option_id=None):
        """
        Обновление варианта ответа по ID.
        """
        if not option_id:
            return JsonResponse({"error": "Option ID is required in URL."}, status=400)

        if not self.get_object_by_id("optionss", option_id):
            return JsonResponse({"error": "Option not found."}, status=404)

        data = request.data

        query = "UPDATE optionss SET value = %s WHERE id = %s RETURNING id, value;"
        try:
            updated_option = BaseSQLHandler.execute_query(
                query, [data["value"], option_id], fetchone=True
            )
        except Exception as e:
            return self.handle_database_error("Unable to update option", e)

        return JsonResponse(
            {"id": updated_option[0], "value": updated_option[1]}, status=200
        )

    @admin_required
    def delete(self, request, option_id=None):
        """
        Удаление варианта ответа по ID.
        """
        if not option_id:
            return JsonResponse({"error": "Option ID is required in URL."}, status=400)

        if not self.get_object_by_id("optionss", option_id):
            return JsonResponse({"error": "Option not found."}, status=404)

        query = "DELETE FROM optionss WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [option_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete option", e)

        return JsonResponse({"detail": "Option deleted successfully."}, status=200)


class TestsQuestionsAPIView(BaseAPIView):
    @admin_required
    def post(self, request):
        """
        Связывание вопроса с тестом.
        """
        data = request.data

        query = """
        INSERT INTO testsquestions (test_id, question_id)
        VALUES (%s, %s)
        RETURNING id, test_id, question_id;
        """
        try:
            link = BaseSQLHandler.execute_query(
                query, [data["test_id"], data["question_id"]], fetchone=True
            )
        except Exception as e:
            return self.handle_database_error("Unable to link test and question", e)

        return JsonResponse(
            {"id": link[0], "test_id": link[1], "question_id": link[2]}, status=201
        )

    @admin_required
    def get(self, request, test_id=None):
        """
        Получение информации о связи вопроса с тестом.
        Если передан link_id — возвращает конкретную связь.
        Если передан test_id — возвращает все вопросы для указанного теста.
        Если параметры не переданы — возвращает все связи.
        """
        if not test_id:
            return JsonResponse({"error": "test_id is required"}, status=400)

        query = """
        SELECT tq.id AS link_id,  -- Добавляем ID связи
            q.id AS question_id,
            q.name AS question_name,
            q.topic_id,
            q.correct_answer_id,
            o.id AS option_id,
            o.value AS option_value
        FROM   testsquestions AS tq
        JOIN   questions      AS q  ON tq.question_id = q.id
        LEFT JOIN questionoptions AS qo ON qo.question_id = q.id
        LEFT JOIN optionss    AS o  ON qo.option_id = o.id
        WHERE  tq.test_id = %s
        ORDER BY q.id, o.id;
        """

        try:
            rows = BaseSQLHandler.execute_query(query, [test_id], fetchall=True)
        except Exception as e:
            return JsonResponse({"error": f"Database error: {e}"}, status=500)

        # rows будет списком кортежей вида:
        # [
        #   (link_id, question_id, question_name, topic_id, correct_answer_id, option_id, option_value),
        #   ...
        # ]
        # Нужно сгруппировать это по question_id.

        questions_map = {}  # словарь { question_id: { ...question_data..., options: [...] } }

        for row in rows:
            (link_id,
            q_id,
            q_name,
            q_topic_id,
            q_correct_answer_id,
            opt_id,
            opt_value) = row

            # Если вопрос ещё не встречался, создаём для него запись:
            if q_id not in questions_map:
                questions_map[q_id] = {
                    "id": q_id,
                    "name": q_name,
                    "topic_id": q_topic_id,
                    "correct_answer_id": q_correct_answer_id,
                    "link_id": link_id,  # Добавляем link_id в структуру вопроса
                    "options": []
                }

            # Если у вопроса есть вариант (opt_id не NULL),
            # добавим его в список options:
            if opt_id:
                questions_map[q_id]["options"].append({
                    "id": opt_id,
                    "value": opt_value,
                    "is_correct": (opt_id == q_correct_answer_id)
                })

        # Преобразуем questions_map.values() к списку
        questions_list = list(questions_map.values())

        return JsonResponse(questions_list, safe=False, status=200)


    @admin_required
    def put(self, request, link_id=None):
        """
        Обновление связи вопроса с тестом по ID.
        """
        if not link_id:
            return JsonResponse({"error": "Link ID is required in URL."}, status=400)

        if not self.get_object_by_id("testsquestions", link_id):
            return JsonResponse({"error": "Link not found."}, status=404)

        data = request.data

        update_fields = []
        values = []

        if "test_id" in data:
            update_fields.append("test_id = %s")
            values.append(data["test_id"])
        if "question_id" in data:
            update_fields.append("question_id = %s")
            values.append(data["question_id"])

        if not update_fields:
            return JsonResponse({"error": "No fields to update."}, status=400)

        query = f"""
        UPDATE testsquestions
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, test_id, question_id;
        """
        values.append(link_id)

        try:
            updated_link = BaseSQLHandler.execute_query(query, values, fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to update link", e)

        return JsonResponse(
            {
                "id": updated_link[0],
                "test_id": updated_link[1],
                "question_id": updated_link[2],
            },
            status=200,
        )

    @admin_required
    def delete(self, request, test_id=None):
        """
        Удаление связи вопроса с тестом по ID.
        """
        link_id = test_id

        if not link_id:
            return JsonResponse({"error": "Link ID is required in URL."}, status=400)

        if not self.get_object_by_id("testsquestions", link_id):
            return JsonResponse({"error": "Link not found."}, status=404)

        query = "DELETE FROM testsquestions WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [link_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete link", e)

        return JsonResponse({"detail": "Link deleted successfully."}, status=200)


class QuestionOptionsAPIView(BaseAPIView):
    @admin_required
    def post(self, request):
        """
        Связывание варианта ответа с вопросом.
        """
        data = request.data

        query = """
        INSERT INTO questionoptions (question_id, option_id)
        VALUES (%s, %s)
        RETURNING id, question_id, option_id;
        """
        try:
            link = BaseSQLHandler.execute_query(
                query, [data["question_id"], data["option_id"]], fetchone=True
            )
        except Exception as e:
            return self.handle_database_error("Unable to link question and option", e)

        return JsonResponse(
            {"id": link[0], "question_id": link[1], "option_id": link[2]}, status=201
        )

    @admin_required
    def get(self, request, link_id=None):
        """
        Получение информации о связях вариантов ответов с вопросами.
        """
        if link_id:
            query = """
            SELECT qo.id, q.name AS question_name, o.value AS option_value
            FROM questionoptions qo
            JOIN questions q ON qo.question_id = q.id
            JOIN optionss o ON qo.option_id = o.id
            WHERE qo.id = %s;
            """
            link = BaseSQLHandler.execute_query(query, [link_id], fetchone=True)
            if not link:
                return JsonResponse({"error": "Link not found."}, status=404)

            return JsonResponse(
                {"id": link[0], "question_name": link[1], "option_value": link[2]},
                status=200,
            )

        query = """
        SELECT qo.id, q.name AS question_name, o.value AS option_value
        FROM questionoptions qo
        JOIN questions q ON qo.question_id = q.id
        JOIN optionss o ON qo.option_id = o.id;
        """
        links = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [
            {"id": link[0], "question_name": link[1], "option_value": link[2]}
            for link in links
        ]
        return JsonResponse(response, safe=False, status=200)

    @admin_required
    def put(self, request, link_id=None):
        """
        Обновление связи варианта ответа с вопросом.
        """
        if not link_id:
            return JsonResponse({"error": "Link ID is required in URL."}, status=400)

        if not self.get_object_by_id("questionoptions", link_id):
            return JsonResponse({"error": "Link not found."}, status=404)

        data = request.data

        update_fields = []
        values = []

        if "question_id" in data:
            update_fields.append("question_id = %s")
            values.append(data["question_id"])
        if "option_id" in data:
            update_fields.append("option_id = %s")
            values.append(data["option_id"])

        if not update_fields:
            return JsonResponse({"error": "No fields to update."}, status=400)

        query = f"""
        UPDATE questionoptions
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, question_id, option_id;
        """
        values.append(link_id)

        try:
            updated_link = BaseSQLHandler.execute_query(query, values, fetchone=True)
        except Exception as e:
            return self.handle_database_error("Unable to update link", e)

        return JsonResponse(
            {
                "id": updated_link[0],
                "question_id": updated_link[1],
                "option_id": updated_link[2],
            },
            status=200,
        )

    @admin_required
    def delete(self, request, link_id=None):
        """
        Удаление связи варианта ответа с вопросом по ID.
        """
        if not link_id:
            return JsonResponse({"error": "Link ID is required in URL."}, status=400)

        if not self.get_object_by_id("questionoptions", link_id):
            return JsonResponse({"error": "Link not found."}, status=404)

        query = "DELETE FROM questionoptions WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [link_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete link", e)

        return JsonResponse({"detail": "Link deleted successfully."}, status=200)


class MaterialsAPIView(BaseAPIView):
    @admin_required
    def post(self, request):
        """
        Создание нового материала с возможностью загрузки файла.
        """
        data = request.POST
        file = request.FILES.get("file")

        # Обработка файла
        file_url = None
        metadata = None
        if file:
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)
            metadata = json.dumps(
                {
                    "original_name": file.name,
                    "size": file.size,
                    "mime_type": file.content_type,
                }
            )

        # SQL-запрос для создания материала
        query = """
        INSERT INTO materials (topic_id, categorymaterials_id, content, file_url, file_metadata)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, topic_id, categorymaterials_id, content, file_url, file_metadata;
        """
        try:
            material = BaseSQLHandler.execute_query(
                query,
                [
                    data.get("topic_id"),
                    data["categorymaterials_id"],
                    data.get("content"),
                    file_url,
                    metadata,
                ],
                fetchone=True,
            )
        except Exception as e:
            return self.handle_database_error("Unable to create material", e)

        return JsonResponse(
            {
                "id": material[0],
                "topic_id": material[1],
                "categorymaterials_id": material[2],
                "content": material[3],
                "file_url": material[4],
                "file_metadata": json.loads(material[5]) if material[5] else None,
            },
            status=201,
        )

    @admin_required
    def get(self, request, material_id=None):
        """
        Получение списка всех материалов или конкретного материала по ID.
        """
        if material_id:
            query = """
            SELECT id, topic_id, categorymaterials_id, content, file_url, file_metadata
            FROM materials
            WHERE id = %s;
            """
            material = BaseSQLHandler.execute_query(query, [material_id], fetchone=True)
            if not material:
                return JsonResponse({"error": "Material not found."}, status=404)

            return JsonResponse(
                {
                    "id": material[0],
                    "topic_id": material[1],
                    "categorymaterials_id": material[2],
                    "content": material[3],
                    "file_url": material[4],
                    "file_metadata": json.loads(material[5]) if material[5] else None,
                },
                status=200,
            )

        query = """
        SELECT id, topic_id, categorymaterials_id, content, file_url, file_metadata
        FROM materials;
        """
        materials = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [
            {
                "id": material[0],
                "topic_id": material[1],
                "categorymaterials_id": material[2],
                "content": material[3],
                "file_url": material[4],
                "file_metadata": json.loads(material[5]) if material[5] else None,
            }
            for material in materials
        ]
        return JsonResponse(response, safe=False, status=200)

    @admin_required
    def put(self, request, material_id=None):
        """
        Обновление информации о материале по ID.
        """
        if not material_id:
            return JsonResponse(
                {"error": "Material ID is required in URL."}, status=400
            )

        if not self.get_object_by_id("materials", material_id):
            return JsonResponse({"error": "Material not found."}, status=404)

        data = request.POST
        file = request.FILES.get("file")

        # Обработка файла (если загружается новый файл)
        file_url = None
        metadata = None
        if file:
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)
            metadata = json.dumps(
                {
                    "original_name": file.name,
                    "size": file.size,
                    "mime_type": file.content_type,
                }
            )

        # Построение SQL-запроса для обновления
        update_fields = []
        values = []

        if "topic_id" in data:
            update_fields.append("topic_id = %s")
            values.append(data.get("topic_id"))
        if "categorymaterials_id" in data:
            update_fields.append("categorymaterials_id = %s")
            values.append(data.get("categorymaterials_id"))
        if "content" in data:
            update_fields.append("content = %s")
            values.append(data.get("content"))
        if file_url:
            update_fields.append("file_url = %s")
            values.append(file_url)
        if metadata:
            update_fields.append("file_metadata = %s")
            values.append(metadata)

        if not update_fields:
            return JsonResponse({"error": "No fields to update."}, status=400)

        query = f"""
        UPDATE materials
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, topic_id, categorymaterials_id, content, file_url, file_metadata;
        """
        values.append(material_id)

        try:
            updated_material = BaseSQLHandler.execute_query(
                query, values, fetchone=True
            )
        except Exception as e:
            return self.handle_database_error("Unable to update material", e)

        return JsonResponse(
            {
                "id": updated_material[0],
                "topic_id": updated_material[1],
                "categorymaterials_id": updated_material[2],
                "content": updated_material[3],
                "file_url": updated_material[4],
                "file_metadata": (
                    json.loads(updated_material[5]) if updated_material[5] else None
                ),
            },
            status=200,
        )

    @admin_required
    def delete(self, request, material_id=None):
        """
        Удаление материала по ID.
        """
        if not material_id:
            return JsonResponse(
                {"error": "Material ID is required in URL."}, status=400
            )

        if not self.get_object_by_id("materials", material_id):
            return JsonResponse({"error": "Material not found."}, status=404)

        # Удаление записи из базы данных
        query = "DELETE FROM materials WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [material_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete material", e)

        return JsonResponse({"detail": "Material deleted successfully."}, status=200)


class UsersModulesAPIView(BaseAPIView):
    @admin_required
    def post(self, request):
        """
        Привязка модуля к пользователю.
        """
        data = request.data

        query = """
        INSERT INTO usersmodules (user_id, module_id)
        VALUES (%s, %s)
        RETURNING id, user_id, module_id;
        """
        try:
            user_module = BaseSQLHandler.execute_query(
                query, [data["user_id"], data["module_id"]], fetchone=True
            )
        except Exception as e:
            return self.handle_database_error("Unable to link user and module", e)

        return JsonResponse(
            {
                "id": user_module[0],
                "user_id": user_module[1],
                "module_id": user_module[2],
            },
            status=201,
        )

    @admin_required
    def get(self, request, link_id=None):
        """
        Получение связей пользователей и модулей.
        """
        if link_id:
            query = """
            SELECT um.id, u.fio AS user_name, m.name AS module_name
            FROM usersmodules AS um
            JOIN users AS u ON um.user_id = u.id
            JOIN modules AS m ON um.module_id = m.id
            WHERE um.id = %s;
            """
            link = BaseSQLHandler.execute_query(query, [link_id], fetchone=True)
            if not link:
                return JsonResponse({"error": "Link not found."}, status=404)

            return JsonResponse(
                {"id": link[0], "user_name": link[1], "module_name": link[2]},
                status=200,
            )

        query = """
        SELECT um.id, u.fio AS user_name, m.name AS module_name
        FROM usersmodules AS um
        JOIN users AS u ON um.user_id = u.id
        JOIN modules AS m ON um.module_id = m.id;
        """
        links = BaseSQLHandler.execute_query(query, fetchall=True)
        response = [
            {"id": link[0], "user_name": link[1], "module_name": link[2]}
            for link in links
        ]
        return JsonResponse(response, safe=False, status=200)

    @admin_required
    def delete(self, request, link_id=None):
        """
        Удаление связи пользователя с модулем по ID.
        """
        if not link_id:
            return JsonResponse({"error": "Link ID is required in URL."}, status=400)

        if not self.get_object_by_id("usersmodules", link_id):
            return JsonResponse({"error": "Link not found."}, status=404)

        query = "DELETE FROM usersmodules WHERE id = %s;"
        try:
            BaseSQLHandler.execute_query(query, [link_id])
        except Exception as e:
            return self.handle_database_error("Unable to delete link", e)

        return JsonResponse({"detail": "Link deleted successfully."}, status=200)
