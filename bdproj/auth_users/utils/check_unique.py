from django.db import connection

def execute_query(query, params=None, fetchone=False, fetchall=False):
    # Пример реализации функции выполнения запроса
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        if fetchone:
            return cursor.fetchone()
        if fetchall:
            return cursor.fetchall()


def validate_unique_field(table, field, value, exclude_id=None):
    """
    Проверяет уникальность значения в указанной таблице.

    :param execute_query_function: Функция для выполнения SQL-запроса.
    :param table: Название таблицы.
    :param field: Название столбца, который проверяется на уникальность.
    :param value: Проверяемое значение.
    :param exclude_id: Идентификатор записи, которая должна быть исключена из проверки (опционально).
    :return: True, если значение уникально, иначе False.
    """
    query = f"SELECT id FROM {table} WHERE {field} = %s"
    params = [value]
    if exclude_id:
        query += " AND id != %s"
        params.append(exclude_id)

    result = execute_query(query, params, fetchone=True)
    return result is None