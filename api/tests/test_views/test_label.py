from typing import Any, Dict, List
from uuid import UUID

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from api.models import Label

User = get_user_model()


class TestLabelViewSet(APITestCase):
    DEFAULT_PASSWORD: str = "test_password"

    def setUp(self) -> None:
        self.client: APIClient = APIClient()

        self.admin: User = User.objects.create_superuser(
            username="admin",
            password=self.DEFAULT_PASSWORD,
            full_name="Admin User",
        )
        self.client.force_authenticate(self.admin)

        self.user1: User = User.objects.create_user(
            username="user1", password=self.DEFAULT_PASSWORD, full_name="User One"
        )
        self.user2: User = User.objects.create_user(
            username="user2", password=self.DEFAULT_PASSWORD, full_name="User Two"
        )

        self.label1: Label = Label.objects.create(owner=self.user1, label="Label 1")
        self.label2: Label = Label.objects.create(owner=self.user2, label="Label 2")

        self.list_url: str = reverse("label-list")

    def test_list_returns_labels_in_desc_order(self) -> None:
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data: List[Dict[str, Any]] = resp.json()
        self.assertGreaterEqual(len(data), 2)

        created_times = [item["created_at"] for item in data]
        self.assertEqual(sorted(created_times, reverse=True), created_times)

    def test_create_label(self) -> None:
        payload: Dict[str, Any] = {
            "label": "New Label",
            "owner": str(self.user1.id),
        }

        resp = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        body: Dict[str, Any] = resp.json()
        created = Label.objects.get(id=body["id"])

        self.assertEqual(created.label, payload["label"])
        self.assertEqual(created.owner, self.user1)
        self.assertIn("created_at", body)
        self.assertIn("modified_at", body)

    def test_create_duplicate_label_for_same_owner_fails(self) -> None:
        payload: Dict[str, Any] = {
            "label": self.label1.label,
            "owner": str(self.user1.id),
        }

        resp = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        body = resp.json()
        self.assertIn("non_field_errors", body)

    def test_retrieve_returns_single_label(self) -> None:
        url: str = reverse("label-detail", kwargs={"pk": str(self.label1.id)})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data: Dict[str, Any] = resp.json()
        self.assertEqual(UUID(data["id"]), self.label1.id)
        self.assertEqual(data["label"], self.label1.label)
        self.assertEqual(UUID(data["owner"]), self.user1.id)

    def test_put_updates_label(self) -> None:
        url: str = reverse("label-detail", kwargs={"pk": str(self.label1.id)})
        payload: Dict[str, Any] = {
            "label": "Updated Label",
            "owner": str(self.user1.id),
        }

        resp = self.client.put(url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.label1.refresh_from_db()
        self.assertEqual(self.label1.label, "Updated Label")

    def test_patch_updates_partial_fields(self) -> None:
        url: str = reverse("label-detail", kwargs={"pk": str(self.label2.id)})

        resp = self.client.patch(url, data={"label": "Patched Label"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.label2.refresh_from_db()
        self.assertEqual(self.label2.label, "Patched Label")

    def test_delete_removes_label(self) -> None:
        url: str = reverse("label-detail", kwargs={"pk": str(self.label2.id)})

        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Label.objects.filter(id=self.label2.id).exists())
