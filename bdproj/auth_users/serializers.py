from rest_framework import serializers


class UserInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fio = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    is_active = serializers.BooleanField()
    role = serializers.CharField(max_length=255)
    level = serializers.CharField(max_length=255)
    entrance_test = serializers.BooleanField()

class UpdateUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fio = serializers.CharField(max_length=255)
    email = serializers.EmailField()


class RegisterUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fio = serializers.CharField(max_length=255)
    email = serializers.EmailField()



class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    role_id = serializers.IntegerField()

