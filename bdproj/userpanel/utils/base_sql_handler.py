from django.db import connection

class BaseSQLHandler:
    @staticmethod
    def execute_query(query, params=None, fetchone=False, fetchall=False):
        """
        Выполняет SQL-запрос с обработкой исключений.
        """
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, params or [])
                if fetchone:
                    return cursor.fetchone()
                if fetchall:
                    return cursor.fetchall()
            except Exception as e:
                raise Exception(f"Database error: {e}")