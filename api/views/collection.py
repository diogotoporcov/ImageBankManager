from rest_framework import viewsets
from api.models.collection import Collection
from api.serializers.collection import CollectionSerializer


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all().order_by("-created_at")
    serializer_class = CollectionSerializer
