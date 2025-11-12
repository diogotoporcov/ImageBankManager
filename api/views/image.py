from rest_framework import viewsets
from api.models.image import Image
from api.serializers.image import ImageSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all().order_by("-created_at")
    serializer_class = ImageSerializer
