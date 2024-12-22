from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fio = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    is_active = serializers.BooleanField()
    role = serializers.CharField(max_length=255)
    level = serializers.CharField(max_length=255)
    entrance_test = serializers.BooleanField()


class RoleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=128)


class LevelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=128)




