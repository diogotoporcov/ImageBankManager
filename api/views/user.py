from rest_framework import viewsets
from api.models.user import User
from api.serializers.user import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
