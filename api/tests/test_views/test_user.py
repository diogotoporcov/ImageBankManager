from typing import Any, Dict, List
from uuid import UUID

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

User = get_user_model()


class TestUserViewSet(APITestCase):
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
            username="user1", password=self.DEFAULT_PASSWORD, full_name="User 1"
        )
        self.user2: User = User.objects.create_user(
            username="user2", password=self.DEFAULT_PASSWORD, full_name="User 2"
        )

        self.list_url: str = reverse("user-list")

    def test_list_returns_users_ordered_by_created_desc(self) -> None:
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data: List[Dict[str, Any]] = resp.json()
        self.assertGreaterEqual(len(data), 2)
        first_id: UUID = UUID(data[0]["id"])
        second_id: UUID = UUID(data[1]["id"])
        self.assertEqual(first_id, self.user2.id)
        self.assertEqual(second_id, self.user1.id)

    def test_create_creates_user_and_hashes_password(self) -> None:
        payload: Dict[str, Any] = {
            "username": "created_user",
            "full_name": "Created User",
            "password": "test_password",
        }
        resp = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        body: Dict[str, Any] = resp.json()
        self.assertNotIn("password", body)
        created = User.objects.get(id=body["id"])
        self.assertTrue(created.check_password("test_password"))

    def test_retrieve_returns_single_user(self) -> None:
        url: str = reverse("user-detail", kwargs={"pk": str(self.user1.id)})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data: Dict[str, Any] = resp.json()
        self.assertEqual(UUID(data["id"]), self.user1.id)

    def test_put_updates_user(self) -> None:
        url: str = reverse("user-detail", kwargs={"pk": str(self.user1.id)})
        payload: Dict[str, Any] = {
            "username": "user1",
            "full_name": "User One Updated",
            "password": "test_password2",
        }
        resp = self.client.put(url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_patch_updates_partial_fields(self) -> None:
        url: str = reverse("user-detail", kwargs={"pk": str(self.user2.id)})
        resp = self.client.patch(url, data={"full_name": "User Two Patched"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.full_name, "User Two Patched")

    def test_delete_removes_user(self) -> None:
        url: str = reverse("user-detail", kwargs={"pk": str(self.user2.id)})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user2.id).exists())
