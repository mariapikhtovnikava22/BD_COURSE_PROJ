from django.db import connection
import psycopg2
from psycopg2.extras import execute_batch

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
            

    @staticmethod
    def execute_many(query, data):
        """
        Выполняет SQL-запрос с множеством параметров.
        
        :param query: SQL-запрос, который нужно выполнить.
        :param data: Список параметров для выполнения запроса.
        """
        try:
            with psycopg2.connect(
                dbname="your_database_name",
                user="your_user",
                password="your_password",
                host="your_host",
                port="your_port"
            ) as conn:
                with conn.cursor() as cursor:
                    execute_batch(cursor, query, data)
                conn.commit()
        except Exception as e:
            print(f"Error executing batch query: {e}")
            raise