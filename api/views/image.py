from rest_framework import viewsets, filters
from api.models.image import Image
from api.serializers.image import ImageSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    filter_backends = [filters.OrderingFilter]
    ordering_fields = [
        "created_at",
        "updated_at",
        "size_bytes",
    ]
    ordering = ["-created_at"]
