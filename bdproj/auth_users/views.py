# from django.db import connection
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.contrib.auth.hashers import make_password

# class RegisterUserAPIView(APIView):
#     def post(self, request):
#         data = request.data
#         query = """
#         INSERT INTO users (fio, email, password, is_active, image)
#         VALUES (%s, %s, %s, %s, %s)
#         RETURNING id, fio, email, image;
#         """
#         hashed_password = make_password(data['password'])

#         with connection.cursor() as cursor:
#             cursor.execute(query, [
#                 data['fio'],
#                 data['email'],
#                 hashed_password,
#                 True,
#                 data.get('image', None),
#             ])
#             user = cursor.fetchone()

#         return Response(
#             {
#                 "id": user[0],
#                 "fio": user[1],
#                 "email": user[2],
#                 "image": user[3],
#             },
#             status=status.HTTP_201_CREATED,
#         )
