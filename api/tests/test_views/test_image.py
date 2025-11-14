from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from api.models import Image, Collection

User = get_user_model()


class TestImageViewSet(APITestCase):
    DEFAULT_PASSWORD = "test_password"

    def setUp(self) -> None:
        self.client: APIClient = APIClient()

        self.admin = User.objects.create_superuser(
            username="admin",
            password=self.DEFAULT_PASSWORD,
            full_name="Admin User",
        )
        self.client.force_authenticate(self.admin)

        self.user1 = User.objects.create_user(
            username="user1", password=self.DEFAULT_PASSWORD, full_name="User One"
        )
        self.user2 = User.objects.create_user(
            username="user2", password=self.DEFAULT_PASSWORD, full_name="User Two"
        )

        self.col1 = Collection.objects.create(owner=self.user1, name="Collection 1")
        self.col2 = Collection.objects.create(owner=self.user2, name="Collection 2")

        self.image1 = Image.objects.create(
            collection=self.col1,
            filename="image1.jpg",
            mime_type="image/jpeg",
            size_bytes=1000,
            labels=["foo"],
        )

        self.image2 = Image.objects.create(
            collection=self.col2,
            filename="image2.jpg",
            mime_type="image/jpeg",
            size_bytes=2000,
            labels=["bar", "baz"],
        )

        self.list_url = reverse("image-list")

    def test_list_returns_images_in_desc_order(self) -> None:
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data: List[Dict[str, Any]] = resp.json()
        self.assertGreaterEqual(len(data), 2)

        created_values = [item["created_at"] for item in data]
        self.assertEqual(sorted(created_values, reverse=True), created_values)

    def test_create_image(self) -> None:
        payload = {
            "collection": str(self.col1.id),
            "filename": "filename.jpg",
            "mime_type": "image/jpeg",
            "size_bytes": 1000,
            "labels": ["x", "y"],
        }

        resp = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        body = resp.json()
        created = Image.objects.get(id=body["id"])

        self.assertEqual(created.owner, self.user1)
        self.assertEqual(created.collection, self.col1)
        self.assertEqual(created.labels, ["x", "y"])

    def test_create_missing_required_fields_fails(self) -> None:
        payload = {
            "collection": str(self.col1.id),
        }
        resp = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("filename", resp.json())

    def test_create_ignores_readonly_fields(self) -> None:
        now = datetime.now(timezone.utc).isoformat()

        payload = {
            "collection": str(self.col1.id),
            "filename": "filename.jpg",
            "mime_type": "image/jpeg",
            "size_bytes": 1000,
            "created_at": now,
            "updated_at": now,
            "labels": ["ignored"],
        }

        resp = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        created = Image.objects.get(id=resp.json()["id"])
        self.assertNotEqual(created.created_at.isoformat(), now)

    def test_retrieve_image(self) -> None:
        url = reverse("image-detail", kwargs={"pk": str(self.image1.id)})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.json()
        self.assertEqual(UUID(data["id"]), self.image1.id)
        self.assertEqual(data["filename"], self.image1.filename)
        self.assertEqual(data["labels"], ["foo"])

    def test_put_updates_image(self) -> None:
        url = reverse("image-detail", kwargs={"pk": str(self.image1.id)})
        payload = {
            "collection": str(self.col1.id),
            "filename": "updated.jpg",
            "mime_type": "image/jpeg",
            "size_bytes": 1000,
            "labels": ["new1", "new2"],
        }

        resp = self.client.put(url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.image1.refresh_from_db()
        self.assertEqual(self.image1.filename, "updated.jpg")
        self.assertEqual(self.image1.size_bytes, 1000)
        self.assertEqual(self.image1.labels, ["new1", "new2"])

    def test_patch_updates_partial_fields(self) -> None:
        url = reverse("image-detail", kwargs={"pk": str(self.image2.id)})

        resp = self.client.patch(url, data={"filename": "patch.jpg"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.image2.refresh_from_db()
        self.assertEqual(self.image2.filename, "patch.jpg")

    def test_delete_removes_image(self) -> None:
        image = Image.objects.create(
            collection=self.col1,
            filename="del.jpg",
            mime_type="image/jpeg",
            size_bytes=10,
            labels=["temp"],
        )
        url = reverse("image-detail", kwargs={"pk": str(image.id)})

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Image.objects.filter(id=image.id).exists())
