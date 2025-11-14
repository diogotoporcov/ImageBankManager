from rest_framework import viewsets, filters
from api.models.collection import Collection
from api.serializers.collection import CollectionSerializer


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    filter_backends = [filters.OrderingFilter]
    ordering_fields = [
        "created_at",
        "updated_at",
    ]

    ordering = ["-created_at"]
