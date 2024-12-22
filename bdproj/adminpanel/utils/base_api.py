from rest_framework.views import APIView
from django.http import JsonResponse
from .base_sql_handler import BaseSQLHandler

class BaseAPIView(APIView):
    def validate_unique_field(self, table, field, value, exclude_id=None):
        """
        Проверяет уникальность значения в указанной таблице.
        """
        query = f"SELECT id FROM {table} WHERE {field} = %s"
        params = [value]
        if exclude_id:
            query += " AND id != %s"
            params.append(exclude_id)
        return BaseSQLHandler.execute_query(query, params, fetchone=True) is None

    def get_object_by_id(self, table, obj_id):
        """
        Получает объект по ID из указанной таблицы.
        """
        query = f"SELECT * FROM {table} WHERE id = %s"
        return BaseSQLHandler.execute_query(query, [obj_id], fetchone=True)

    def handle_database_error(self, error_message, exception):
        """
        Обрабатывает ошибки базы данных.
        """
        return JsonResponse({"error": f"{error_message}: {exception}"}, status=400)
