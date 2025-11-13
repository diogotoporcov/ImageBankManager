from typing import Any, Dict, List
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from api.models import Collection, Label, Image

User = get_user_model()


class TestCollectionViewSet(APITestCase):
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

        self.collection1 = Collection.objects.create(owner=self.user1, name="Collection 1")
        self.collection2 = Collection.objects.create(owner=self.user2, name="Collection 2")

        self.label = Label.objects.create(owner=self.user1, label="Test Label")
        self.image = Image.objects.create(
            collection=self.collection1,
            filename="filename.jpg",
            mime_type="image/jpeg",
            size_bytes=1234,
        )

        self.list_url = reverse("collection-list")

    def test_list_returns_collections_in_desc_order(self) -> None:
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data: List[Dict[str, Any]] = resp.json()
        self.assertGreaterEqual(len(data), 2)

        created_values = [item["created_at"] for item in data]
        self.assertEqual(sorted(created_values, reverse=True), created_values)

    def test_create_collection(self) -> None:
        payload = {
            "name": "CreatedCol",
            "owner": self.user1.id,
            "label_ids": [self.label.id],
            "image_ids": [self.image.id],
        }

        print(self.user1.id == self.label.owner.id == self.image.owner.id)

        resp = self.client.post(self.list_url, data=payload, format="json")
        body = resp.json()
        print("START OIE")
        print(body)
        print("END OIE")

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        created = Collection.objects.get(id=body["id"])

        self.assertEqual(created.name, "CreatedCol")
        self.assertEqual(created.owner, self.user1)
        self.assertIn(self.label, created.labels.all())
        self.assertIn(self.image, created.images.all())

    def test_create_ignores_readonly_fields(self) -> None:
        payload = {
            "name": "ColIgnore",
            "owner": str(self.user1.id),
            "is_default": True,
        }

        resp = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        created = Collection.objects.get(id=resp.json()["id"])
        self.assertFalse(created.is_default)

    def test_create_missing_required_fields_fails(self) -> None:
        payload = {"owner": str(self.user1.id)}
        resp = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", resp.json())

    def test_retrieve_collection(self) -> None:
        url = reverse("collection-detail", kwargs={"pk": str(self.collection1.id)})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.json()
        self.assertEqual(UUID(data["id"]), self.collection1.id)
        self.assertEqual(data["name"], self.collection1.name)

    def test_put_updates_collection(self) -> None:
        url = reverse("collection-detail", kwargs={"pk": str(self.collection1.id)})
        payload = {
            "name": "C1 Updated",
            "owner": str(self.user1.id),
        }

        resp = self.client.put(url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.collection1.refresh_from_db()
        self.assertEqual(self.collection1.name, "C1 Updated")

    def test_put_cannot_set_is_default(self) -> None:
        url = reverse("collection-detail", kwargs={"pk": str(self.collection1.id)})
        payload = {
            "name": "NewName",
            "owner": str(self.user1.id),
            "is_default": True,
        }

        resp = self.client.put(url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.collection1.refresh_from_db()
        self.assertFalse(self.collection1.is_default)
        self.assertEqual(self.collection1.name, "NewName")

    def test_patch_updates_partial_fields(self) -> None:
        url = reverse("collection-detail", kwargs={"pk": str(self.collection2.id)})

        resp = self.client.patch(url, data={"name": "C2 Patched"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.collection2.refresh_from_db()
        self.assertEqual(self.collection2.name, "C2 Patched")

    def test_delete_removes_collection(self) -> None:
        col = Collection.objects.create(owner=self.user1, name="DeleteMe")
        url = reverse("collection-detail", kwargs={"pk": str(col.id)})

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Collection.objects.filter(id=col.id).exists())

    def test_delete_fails_for_default_collection(self) -> None:
        default_col = self.user1.collections.filter(is_default=True).first()
        url = reverse("collection-detail", kwargs={"pk": str(default_col.id)})

        with self.assertRaises(ValidationError):
            self.client.delete(url)

    def test_create_second_default_collection_disallowed(self) -> None:
        payload = {
            "name": "AnotherDefault",
            "owner": str(self.user1.id),
            "is_default": True,
        }

        resp = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_col = Collection.objects.get(id=resp.json()["id"])
        self.assertFalse(new_col.is_default)

        default_count = Collection.objects.filter(owner=self.user1, is_default=True).count()
        self.assertEqual(default_count, 1)
