from django.test import TestCase
from django.contrib.auth import get_user_model
from api.serializers.user import UserSerializer

User = get_user_model()


class TestUserSerializer(TestCase):
    DEFAULT_USERNAME = "serializer_user"
    DEFAULT_FULL_NAME = "Test User"
    DEFAULT_PASSWORD = "test_password"

    def setUp(self):
        self.valid_data = {
            "username": self.DEFAULT_USERNAME,
            "full_name": self.DEFAULT_FULL_NAME,
            "password": self.DEFAULT_PASSWORD,
        }

    def test_valid_serialization_and_creation(self):
        serializer = UserSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        user = serializer.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, self.DEFAULT_USERNAME)
        self.assertEqual(user.full_name, self.DEFAULT_FULL_NAME)
        self.assertTrue(user.check_password(self.DEFAULT_PASSWORD))
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)

    def test_password_is_write_only(self):
        serializer = UserSerializer(data=self.valid_data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        self.assertNotIn("password", serialized_data)
        self.assertIn("username", serialized_data)

    def test_missing_required_fields(self):
        incomplete_data = {
            "username": "missing_fields_user",
            "password": self.DEFAULT_PASSWORD,
        }
        serializer = UserSerializer(data=incomplete_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("full_name", serializer.errors)

    def test_duplicate_username_raises_error(self):
        User.objects.create_user(
            username=self.DEFAULT_USERNAME,
            password="password123",
            full_name="Existing User"
        )
        serializer = UserSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_password_is_not_stored_in_plain_text(self):
        serializer = UserSerializer(data=self.valid_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        self.assertNotEqual(user.password, self.DEFAULT_PASSWORD)
        self.assertTrue(user.password.startswith("argon2"))
