from rest_framework import serializers


class UserInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fio = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    is_active = serializers.BooleanField()


class RegisterUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fio = serializers.CharField(max_length=255)
    email = serializers.EmailField()



class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
