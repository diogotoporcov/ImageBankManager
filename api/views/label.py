from rest_framework import viewsets
from api.models.label import Label
from api.serializers.label import LabelSerializer


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all().order_by("-created_at")
    serializer_class = LabelSerializer
