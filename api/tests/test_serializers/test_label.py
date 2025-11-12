from datetime import datetime, timezone, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import Label
from api.serializers.label import LabelSerializer

User = get_user_model()


class TestLabelSerializer(TestCase):
    DEFAULT_USERNAME = "label_owner"
    DEFAULT_PASSWORD = "test_password"
    DEFAULT_FULL_NAME = "Label Owner"
    DEFAULT_LABEL = "Test Label"

    def setUp(self):
        self.user = User.objects.create_user(
            username=self.DEFAULT_USERNAME,
            password=self.DEFAULT_PASSWORD,
            full_name=self.DEFAULT_FULL_NAME,
        )

        self.valid_data = {
            "label": self.DEFAULT_LABEL,
            "owner": self.user.id,
        }

    def test_valid_serialization_and_creation(self):
        serializer = LabelSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        label = serializer.save()
        self.assertIsInstance(label, Label)
        self.assertEqual(label.label, self.DEFAULT_LABEL)
        self.assertEqual(label.owner, self.user)
        self.assertIsNotNone(label.created_at)
        self.assertIsNotNone(label.modified_at)

    def test_read_only_fields_ignored_on_input(self):
        now = datetime.now(timezone.utc)
        data_with_readonly = {
            **self.valid_data,
            "id": "id",
            "created_at": (now - timedelta(days=1)).isoformat(),
            "modified_at": now.isoformat(),
        }

        serializer = LabelSerializer(data=data_with_readonly)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        label = serializer.save()

        self.assertNotEqual(str(label.id), "id")
        self.assertNotEqual(label.created_at.isoformat(), data_with_readonly["created_at"])
        self.assertNotEqual(label.modified_at.isoformat(), data_with_readonly["modified_at"])

    def test_missing_required_fields(self):
        invalid_data = {"owner": self.user.id}
        serializer = LabelSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("label", serializer.errors)

    def test_duplicate_label_per_owner_not_allowed(self):
        Label.objects.create(owner=self.user, label=self.DEFAULT_LABEL)
        serializer = LabelSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_serialized_output_contains_expected_fields(self):
        label = Label.objects.create(owner=self.user, label=self.DEFAULT_LABEL)
        serializer = LabelSerializer(label)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("label", data)
        self.assertIn("owner", data)
        self.assertIn("created_at", data)
        self.assertIn("modified_at", data)
        self.assertEqual(data["label"], self.DEFAULT_LABEL)
        self.assertEqual(data["owner"], self.user.id)
