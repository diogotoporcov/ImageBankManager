from rest_framework import routers
from api.views import UserViewSet, CollectionViewSet, ImageViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"collections", CollectionViewSet)
router.register(r"images", ImageViewSet)

urlpatterns = router.urls
