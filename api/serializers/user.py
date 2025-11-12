from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from api.models.user import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "full_name",
            "password",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data["password_hash"] = make_password(password)
        return super().create(validated_data)

