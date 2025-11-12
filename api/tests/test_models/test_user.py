import uuid
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUserModel(TestCase):
    DEFAULT_PASSWORD = "test_password"
    DEFAULT_FULL_NAME = "Test User Full Name"

    def test_user_creation(self):
        user = User.objects.create_user(
            username="test_user",
            password=self.DEFAULT_PASSWORD,
            full_name=self.DEFAULT_FULL_NAME
        )

        self.assertIsInstance(user.id, uuid.UUID)
        self.assertEqual(user.username, "test_user")
        self.assertEqual(user.full_name, self.DEFAULT_FULL_NAME)
        self.assertTrue(user.check_password(self.DEFAULT_PASSWORD))
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)

    def test_str_representation(self):
        username = "test_user_str_repr"
        user = User.objects.create_user(
            username=username,
            password=self.DEFAULT_PASSWORD,
            full_name=self.DEFAULT_FULL_NAME
        )

        self.assertEqual(str(user), username)

    def test_auto_timestamps(self):
        user = User.objects.create_user(
            username="test_user_timestamp",
            password=self.DEFAULT_PASSWORD,
            full_name=self.DEFAULT_FULL_NAME
        )

        self.assertAlmostEqual(
            user.updated_at.timestamp(),
            timezone.now().timestamp(),
            delta=0.25
        )

        user.full_name = self.DEFAULT_FULL_NAME + " Update"
        user.save()

        self.assertLessEqual(
            user.created_at,
            user.updated_at
        )

    def test_primary_keu_is_uuid_and_unique(self):
        user1 = User.objects.create_user(
            username="test_user_pk1",
            password=self.DEFAULT_PASSWORD,
            full_name=self.DEFAULT_FULL_NAME
        )
        user2 = User.objects.create_user(
            username="test_user_pk2",
            password=self.DEFAULT_PASSWORD,
            full_name=self.DEFAULT_FULL_NAME
        )

        self.assertIsInstance(user1.id, uuid.UUID)
        self.assertIsInstance(user2.id, uuid.UUID)
        self.assertNotEqual(user1.id, user2.id)
