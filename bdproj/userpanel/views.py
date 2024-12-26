from django.db.models import Q
from .utils.required import isAuthorized
from .utils.base_sql_handler import BaseSQLHandler
from django.http import JsonResponse
from rest_framework.views import APIView
import random
from django.db import connection
from collections import defaultdict
import psycopg2
from psycopg2.extras import execute_batch
from django.http import JsonResponse
from django.db import connection

def execute_query(query, params=None, fetchall=False, fetchone=False):
    """
    Выполнение SQL-запроса.
    """
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        if fetchall:
            return cursor.fetchall()
        if fetchone:
            return cursor.fetchone()
        return None

def execute_many(query, data):
    """
    Выполняет SQL-запрос с множеством параметров.
    """
    with connection.cursor() as cursor:
        execute_batch(cursor, query, data)


class EntranceTestAPIView(APIView):


    @isAuthorized
    def get(self, request):
        """
        Генерация вступительного теста или возврат списка модулей.
        """
        user_id = request.user_id

        # Проверка существования пользователя
        user_query = """
            SELECT id, entrance_test FROM users WHERE id = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(user_query, [user_id])
            user = cursor.fetchone()

        if not user:
            return JsonResponse({"error": "User not found."}, status=404)

        # Если тест уже пройден, возвращаем список модулей
        if user[1]:
            modules_query = """
                SELECT id, name, description FROM modules;
            """
            with connection.cursor() as cursor:
                cursor.execute(modules_query)
                modules = cursor.fetchall()
                modules_list = [{"id": m[0], "name": m[1], "description": m[2]} for m in modules]
            return JsonResponse({"status": "modules", "modules": modules_list}, status=200)

        # Генерация теста, если он не пройден
        try:
            # Запрос для получения вопросов и их вариантов
            questions_with_options_query = """
                SELECT 
                    q.id AS question_id, 
                    q.name AS question_name, 
                    t.id AS topic_id, 
                    t.name AS topic_name, 
                    mods.level_id AS level_id,
                    o.id AS option_id,
                    o.value AS option_text,
                    CASE WHEN q.correct_answer_id = o.id THEN TRUE ELSE FALSE END AS is_correct
                FROM 
                    TestsQuestions tq
                JOIN 
                    Questions q ON tq.question_id = q.id
                JOIN 
                    Topics t ON q.topic_id = t.id
                JOIN 
                    Tests ts ON tq.test_id = ts.id
                JOIN 
                    Modules mods ON t.module_id = mods.id
                JOIN 
                    QuestionOptions qo ON q.id = qo.question_id
                JOIN 
                    Optionss o ON qo.option_id = o.id
                WHERE 
                    ts.module_id = 37;
            """

            with connection.cursor() as cursor:
                cursor.execute(questions_with_options_query)
                rows = cursor.fetchall()

            # Группируем вопросы и их варианты ответов
            questions_map = {}
            for row in rows:
                question_id = row[0]
                if question_id not in questions_map:
                    questions_map[question_id] = {
                        "question_id": question_id,
                        "question_name": row[1],
                        "topic_id": row[2],
                        "topic_name": row[3],
                        "level_id": row[4],
                        "options": []
                    }
                # Добавляем варианты ответов
                questions_map[question_id]["options"].append({
                    "option_id": row[5],
                    "option_text": row[6],
                    "is_correct": row[7],
                })

            # Выбираем 10 случайных вопросов из разных уровней и тем
            questions_by_level = defaultdict(list)
            for question in questions_map.values():
                questions_by_level[question["level_id"]].append(question)

            selected_questions = []
            for level_id, questions in questions_by_level.items():
                random.shuffle(questions)
                selected_questions.extend(questions[:2])  # Берём 2 вопроса с каждого уровня

            # Если 10 вопросов ещё нет, добираем случайными
            all_questions = list(questions_map.values())
            random.shuffle(all_questions)
            while len(selected_questions) < 10 and all_questions:
                question = all_questions.pop(0)
                if question not in selected_questions:
                    selected_questions.append(question)

            # Возвращаем результат
            return JsonResponse({"status": "test", "test": selected_questions}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        


    @isAuthorized
    def post(self, request):
        """
        Обработка результатов теста с учётом динамического количества уровней.
        """
        user_id = request.user_id
        answers = request.data.get("answers", [])

        if not answers:
            return JsonResponse({"error": "No answers provided"}, status=400)

        # Получаем все вопросы и уровни
        questions_query = """
            SELECT q.id, m.level_id
            FROM questions q
            JOIN topics t ON q.topic_id = t.id
            JOIN modules m ON t.module_id = m.id
        """
        questions_data = execute_query(questions_query, fetchall=True)

        # Создаём словарь для сопоставления вопросов и уровней
        question_levels = {}
        level_set = set()
        for q_id, level_id in questions_data:
            question_levels[q_id] = level_id
            level_set.add(level_id)

        # Инициализируем счётчики правильных ответов и общего количества вопросов по уровням
        correct_counts = {level: 0 for level in level_set}
        total_counts = {level: 0 for level in level_set}

        # Проверяем правильность ответов и подсчитываем
        for answer in answers:
            question_id = answer.get("question_id")
            selected_option_id = answer.get("selected_option_id")

            if question_id not in question_levels:
                continue  # Пропускаем вопросы без уровня

            level_id = question_levels[question_id]
            total_counts[level_id] += 1  # Увеличиваем общее количество вопросов этого уровня

            query = """
            SELECT correct_answer_id FROM questions WHERE id = %s;
            """
            correct_answer_id = execute_query(query, [question_id], fetchone=True)
            if correct_answer_id and correct_answer_id[0] == selected_option_id:
                correct_counts[level_id] += 1  # Увеличиваем количество правильных ответов уровня

        # Вычисляем процент правильных ответов по уровням
        level_scores = {
            level: (correct_counts[level] / total_counts[level] * 100) if total_counts[level] > 0 else 0
            for level in total_counts
        }

        # Определение уровня на основе правильных ответов
        sorted_levels = sorted(level_scores.keys())  # Уровни сортируются по возрастанию
        student_level = 1  # Базовый уровень
        for level in sorted_levels:
            if level_scores[level] >= 70:  # Если студент правильно отвечает на 70% вопросов уровня
                student_level = level
            else:
                break  # Если уровень не достигнут, выходим из цикла

        # Обновляем статус теста и уровень для пользователя
        update_query = """
        UPDATE users SET entrance_test = TRUE, level_id = %s WHERE id = %s;
        """
        execute_query(update_query, [student_level, user_id])

        # Получаем модули, соответствующие уровню студента
        modules_query = """
            SELECT id FROM modules WHERE level_id = %s;
        """
        modules = execute_query(modules_query, [student_level], fetchall=True)

        # Вставляем данные в таблицу UsersModules
        if modules:
            user_modules_data = [(user_id, module[0]) for module in modules]
            insert_query = """
                INSERT INTO UsersModules (user_id, module_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """
            execute_many(insert_query, user_modules_data)

        return JsonResponse({
            "status": "completed",
            "correct_counts": correct_counts,
            "level_scores": level_scores,
            "level": student_level,
            "modules_assigned": [module[0] for module in modules],
        }, status=200)



class UserModulesAPIView(APIView):

    @isAuthorized
    def get(self, request):
        user_id = request.user_id

        try:
            # SQL-запрос для получения модулей пользователя вместе с их темами
            query = """
                SELECT 
                    m.id AS module_id, 
                    m.name AS module_name, 
                    m.description AS module_description,
                    t.id AS topic_id,
                    t.name AS topic_name,
                    t.description AS topic_description
                FROM UsersModules um
                JOIN Modules m ON um.module_id = m.id
                LEFT JOIN Topics t ON t.module_id = m.id
                WHERE um.user_id = %s
                ORDER BY m.id, t.id;
            """
            with connection.cursor() as cursor:
                cursor.execute(query, [user_id])
                data = cursor.fetchall()

            # Формируем список модулей с темами
            modules_dict = {}
            for row in data:
                module_id, module_name, module_description, topic_id, topic_name, topic_description = row
                
                if module_id not in modules_dict:
                    modules_dict[module_id] = {
                        "id": module_id,
                        "name": module_name,
                        "description": module_description,
                        "topics": []
                    }
                
                if topic_id:  # Если у модуля есть темы
                    modules_dict[module_id]["topics"].append({
                        "id": topic_id,
                        "name": topic_name,
                        "description": topic_description
                    })

            modules_list = list(modules_dict.values())

            return JsonResponse({"modules": modules_list}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        

class ModuleTopicsTestsView(APIView):

    @isAuthorized
    def get(self, request):
        user_id = request.user_id

        # Шаг 1: Выполняем JOIN для получения модулей и их тем,
        #         только без лишних таблиц, чтобы не создавать дубликаты
        query = """
            SELECT 
                m.id AS module_id,
                m.name AS module_name,
                m.description AS module_description,
                t.id AS topic_id,
                t.name AS topic_name,
                t.description AS topic_description
            FROM UsersModules um
            JOIN Modules m ON um.module_id = m.id
            LEFT JOIN Topics t ON t.module_id = m.id
            WHERE um.user_id = %s
            ORDER BY m.id, t.id
        """

        with connection.cursor() as cursor:
            cursor.execute(query, [user_id])
            rows = cursor.fetchall()

        # rows может выглядеть так:
        # [
        #   (module_id, module_name, module_description, topic_id, topic_name, topic_description),
        #   (module_id, module_name, module_description, topic_id, topic_name, topic_description),
        #   ...
        # ]

        # Шаг 2: Собираем данные в структуру { module_id: { ...info..., topics: { topic_id: {...} } } }
        modules_dict = {}  # словарь по module_id

        for row in rows:
            module_id, module_name, module_description, topic_id, topic_name, topic_description = row

            # Если этого модуля ещё нет в словаре — создаём
            if module_id not in modules_dict:
                modules_dict[module_id] = {
                    "id": module_id,
                    "name": module_name,
                    "description": module_description,
                    "topics": {}
                }

            # Если у модуля есть тема
            if topic_id:
                # Проверим, нет ли её уже
                if topic_id not in modules_dict[module_id]["topics"]:
                    modules_dict[module_id]["topics"][topic_id] = {
                        "id": topic_id,
                        "name": topic_name,
                        "description": topic_description
                    }
                # Если вдруг возникнут дубликаты, здесь мы не добавляем повторно

        # Шаг 3: Преобразуем словарь в список (и «topics» также делаем списком)
        result = []
        for m_id, m_data in modules_dict.items():
            module_topics_list = list(m_data["topics"].values())
            # Заменяем словарь topics на список
            m_data["topics"] = module_topics_list
            result.append(m_data)

        # Шаг 4: Возвращаем в JSON
        return JsonResponse({"modules": result}, status=200, safe=False)
    


class ModuleTestAPIView(APIView):
    
    @isAuthorized
    def get(self, request, module_id):
        """
        Получить тест для конкретного модуля
        """
        try:
            query = """
                SELECT 
                    ts.id AS test_id,
                    ts.name AS test_name,
                    q.id AS question_id,
                    q.name AS question_name,
                    t.id AS topic_id,
                    t.name AS topic_name,
                    mods.level_id AS level_id,
                    o.id AS option_id,
                    o.value AS option_text,
                    CASE WHEN q.correct_answer_id = o.id THEN TRUE ELSE FALSE END AS is_correct
                FROM TestsQuestions tq
                JOIN Questions q ON tq.question_id = q.id
                JOIN Topics t ON q.topic_id = t.id
                JOIN Tests ts ON tq.test_id = ts.id
                JOIN Modules mods ON t.module_id = mods.id
                JOIN QuestionOptions qo ON q.id = qo.question_id
                JOIN Optionss o ON qo.option_id = o.id
                WHERE ts.module_id = %s;
            """

            with connection.cursor() as cursor:
                cursor.execute(query, [module_id])
                data = cursor.fetchall()

            # Формируем структуру теста
            test = { "id": None, "name": None, "questions": [] }
            questions_map = {}

            for row in data:
                (
                    test_id, test_name,
                    question_id, question_text,
                    topic_id, topic_name,
                    level_id,
                    option_id, option_text,
                    is_correct
                ) = row

                # Инициализируем test (один на модуль)
                if test["id"] is None:
                    test["id"] = test_id
                    test["name"] = test_name

                # Инициализируем вопрос, если его ещё нет
                if question_id not in questions_map:
                    questions_map[question_id] = {
                        "id": question_id,
                        "name": question_text,
                        "topic_id": topic_id,
                        "topic_name": topic_name,
                        "correct_answer_id": None,
                        "options": []
                    }
                    test["questions"].append(questions_map[question_id])

                # Если вариант — корректный, запомним его id
                if is_correct:
                    questions_map[question_id]["correct_answer_id"] = option_id

                # Добавляем вариант ответа (если он не null)
                if option_id:
                    questions_map[question_id]["options"].append({
                        "id": option_id,
                        "text": option_text
                    })

            return JsonResponse(test, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class SubmitModuleTestAPIView(APIView):
    """
    POST-запрос для отправки ответов теста модуля.
    Принимает JSON:
    {
      "answers": [
        {"question_id": 101, "selected_option_id": 505},
        ...
      ]
    }
    """
    @isAuthorized
    def post(self, request, module_id):

        user_id = request.user_id
        data = request.data
        print(request)
        answers = data.get("answers", [])

        if not answers:
            return JsonResponse({"error": "No answers provided"}, status=400)

        try:
            # 1) Находим тест, связанный с этим модулем.
            #    (Предполагается, что "module_id" -> таблица tests -> {test}, 
            #     или "tests" может быть несколько. Ниже — упрощённый вариант.)
            test_query = """
                SELECT t.id, t.name
                FROM tests t
                WHERE t.module_id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(test_query, [module_id])
                test_row = cursor.fetchone()

            if not test_row:
                return JsonResponse({"error": "No test found for this module."}, status=404)

            test_id, test_name = test_row

            # 2) Подсчитываем, сколько ответов правильных
            #    Для этого нам нужно для каждого question_id узнать correct_answer_id,
            #    и сравнить с selected_option_id.
            correct_count = 0
            total_questions = len(answers)

            for ans in answers:
                q_id = ans.get("question_id")
                selected_opt = ans.get("selected_option_id")

                # достаём correct_answer_id:
                correct_query = """
                    SELECT correct_answer_id
                    FROM questions
                    WHERE id = %s
                """
                with connection.cursor() as cursor:
                    cursor.execute(correct_query, [q_id])
                    row = cursor.fetchone()
                if not row:
                    # question не найден — пропускаем или считаем неверным
                    continue

                correct_answer_id = row[0]
                if correct_answer_id == selected_opt:
                    correct_count += 1

            # 3) Вычисляем успешность (например, если верно >= 70%, считаем "пройден")
            score_percent = (correct_count / total_questions) * 100 if total_questions > 0 else 0
            is_passed = (score_percent >= 70.0)

            # 4) Обновляем/вставляем запись в UserTestProgress
            #    Проверяем, есть ли уже запись user_id + test_id
            check_query = """
                SELECT id, attempts 
                FROM usertestprogress
                WHERE user_id = %s AND test_id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(check_query, [user_id, test_id])
                utp_row = cursor.fetchone()

            if utp_row:
                # уже есть запись — обновим
                utp_id, old_attempts = utp_row
                new_attempts = old_attempts + 1

                update_utp_query = """
                    UPDATE usertestprogress
                    SET attempts = %s,
                        correct_answers = %s,
                        is_passed = %s
                    WHERE id = %s
                """
                with connection.cursor() as cursor:
                    cursor.execute(update_utp_query, [new_attempts, correct_count, is_passed, utp_id])
            else:
                # вставляем новую запись
                insert_utp_query = """
                    INSERT INTO usertestprogress (user_id, test_id, attempts, correct_answers, is_passed)
                    VALUES (%s, %s, 1, %s, %s)
                """
                with connection.cursor() as cursor:
                    cursor.execute(insert_utp_query, [user_id, test_id, correct_count, is_passed])

            # 5) Обновляем CourseProgress (modules_complite, completion_percentage, etc.)
            #    Логика:  
            #      - Посчитаем, сколько тестов в курсе всего, 
            #        или сколько *модулей* (test_id) — "пройдено" is_passed
            #      - modules_complite = count of usertestprogress.is_passed for user
            #        (только те tests, которые относятся к курсу, 
            #         если курс = набор всех modules)
            #      - completion_percentage = (modules_complite / totalModulesInCourse) * 100
            #      - is_complite_course = True, если modules_complite == totalModulesInCourse

            #   Ниже — очень упрощённый вариант: считаем, что "course" = все modules. 
            #   Или у вас 1 курс. 
            #   (Если курсов несколько, нужна более сложная логика.)

            # 5.1) Узнаём общее количество тестов (или модулей) 
            #      (в примере предполагаем 4 modules => 4 tests)
            total_mod_tests_query = """
                SELECT count(*) 
                FROM tests
                WHERE module_id IN (SELECT id FROM modules)
            """
            with connection.cursor() as cursor:
                cursor.execute(total_mod_tests_query)
                total_tests = cursor.fetchone()[0] or 0

            # 5.2) Узнаём, сколько tests у пользователя is_passed = true
            passed_tests_query = """
                SELECT count(*)
                FROM usertestprogress
                WHERE user_id = %s AND is_passed = true
                AND test_id IN (SELECT id FROM tests WHERE module_id IN (SELECT id FROM modules))
            """
            with connection.cursor() as cursor:
                cursor.execute(passed_tests_query, [user_id])
                passed_count = cursor.fetchone()[0] or 0

            # 5.3) Вычисляем completion_percentage
            completion_percentage = 0.0
            if total_tests > 0:
                completion_percentage = (passed_count / total_tests) * 100

            # 5.4) is_complite_course = completion_percentage >= 100
            is_complite_course = (completion_percentage >= 100)

            # 5.5) Обновляем/вставляем запись в CourseProgress
            #     Проверяем, есть ли уже CourseProgress (user_id)
            cp_query = """
                SELECT id FROM courseprogress WHERE user_id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(cp_query, [user_id])
                cp_row = cursor.fetchone()

            if cp_row:
                cp_id = cp_row[0]
                update_cp_query = """
                    UPDATE courseprogress
                    SET is_complite_course = %s,
                        completion_percentage = %s,
                        modules_complite = %s
                    WHERE id = %s
                """
                with connection.cursor() as cursor:
                    cursor.execute(update_cp_query, 
                        [is_complite_course, completion_percentage, passed_count, cp_id])
            else:
                insert_cp_query = """
                    INSERT INTO courseprogress (user_id, is_complite_course, completion_percentage, modules_complite)
                    VALUES (%s, %s, %s, %s)
                """
                with connection.cursor() as cursor:
                    cursor.execute(insert_cp_query, 
                        [user_id, is_complite_course, completion_percentage, passed_count])

            # 6) Дополнительно, если «все тесты текущего уровня» пройдены — повышаем уровень
            #    Можно хранить user.level_id, 
            #    или user -> Users.level_id. Логика может быть сложнее. 
            #    Ниже — упрощённый пример: 
            #      - смотрим, есть ли ещё тесты (modules) c level = user.level_id, 
            #        все ли они "is_passed"? Если да — user.level_id += 1
            #    (Подразумевается, что Modules хранит level_id, 
            #    a Users хранит текущий level_id.)
            #    Код может выглядеть так:

            #   6.1) Узнаём текущий уровень пользователя
            user_level_query = """
                SELECT level_id
                FROM users
                WHERE id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(user_level_query, [user_id])
                row_ul = cursor.fetchone()
            if row_ul:
                current_level_id = row_ul[0]
                if current_level_id:
                    # Проверяем, есть ли ещё тесты (modules) с level_id = current_level_id, 
                    # которые не пройдены.
                    check_level_query = """
                        SELECT count(*) 
                        FROM tests t
                        JOIN modules m ON t.module_id = m.id
                        WHERE m.level_id = %s
                          AND t.id NOT IN (
                             SELECT test_id 
                             FROM usertestprogress 
                             WHERE user_id = %s AND is_passed = true
                          )
                    """
                    with connection.cursor() as cursor:
                        cursor.execute(check_level_query, [current_level_id, user_id])
                        not_passed_count = cursor.fetchone()[0] or 0

                    if not_passed_count == 0:
                        # Все тесты этого уровня пройдены — повысить уровень
                        # (нужно определить, как вы определяете следующий уровень: level_id + 1?)
                        # Или искать «следующий» уровень. Упростим: +1
                        next_level_id = current_level_id + 1

                        update_level_query = """
                            UPDATE users
                            SET level_id = %s
                            WHERE id = %s
                        """
                        with connection.cursor() as cursor:
                            cursor.execute(update_level_query, [next_level_id, user_id])

            # Возвращаем результат
            result_data = {
                "score_percent": score_percent,
                "correct_count": correct_count,
                "total_questions": total_questions,
                "is_passed": is_passed,
                "completion_percentage": completion_percentage,
                "is_complite_course": is_complite_course
            }
            return JsonResponse(result_data, status=200)

        except Exception as e:
            print("Error in SubmitModuleTest:", e)
            return JsonResponse({"error": str(e)}, status=500)