from django.db.models import Q
from .utils.required import isAuthorized
from .utils.base_sql_handler import BaseSQLHandler
from django.http import JsonResponse
from rest_framework.views import APIView
import random
from django.db import connection
from collections import defaultdict


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
        Обработка результатов теста.
        """
        user_id = request.user_id
        print(request)
        answers = request.data.get("answers", [])

        if not answers:
            return JsonResponse({"error": "No answers provided"}, status=400)

        # Проверяем правильность ответов
        correct_count = 0
        for answer in answers:
            question_id = answer.get("question_id")
            selected_option_id = answer.get("selected_option_id")

            query = """
            SELECT correct_answer_id FROM questions WHERE id = %s;
            """
            correct_answer_id = BaseSQLHandler.execute_query(query, [question_id], fetchone=True)
            if correct_answer_id and correct_answer_id[0] == selected_option_id:
                correct_count += 1
                
        print(correct_count)
        # Вычисляем процент правильных ответов
        score = (correct_count / 10) * 100

        # Обновляем статус теста для пользователя
        update_query = """
        UPDATE users SET entrance_test = TRUE WHERE id = %s;
        """
        BaseSQLHandler.execute_query(update_query, [user_id])

        return JsonResponse({"status": "completed", "score": score}, status=200)

