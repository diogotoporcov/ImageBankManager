import uuid
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from api.models import Label

User = get_user_model()


class TestLabelModel(TestCase):
    DEFAULT_LABEL = "Test Label"

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_label_owner",
            password="test_password",
            full_name="Test Label Owner"
        )

    def test_label_creation(self):
        label = Label.objects.create(
            owner=self.user,
            label=self.DEFAULT_LABEL
        )

        self.assertIsInstance(label.id, uuid.UUID)
        self.assertEqual(label.label, self.DEFAULT_LABEL)
        self.assertEqual(label.owner, self.user)
        self.assertIsNotNone(label.created_at)
        self.assertIsNotNone(label.modified_at)

    def test_str_representation(self):
        label = Label.objects.create(
            owner=self.user,
            label=self.DEFAULT_LABEL
        )

        expected = f"{label.label} ({self.user.username})"
        self.assertEqual(str(label), expected)

    def test_auto_timestamps(self):
        label = Label.objects.create(
            owner=self.user,
            label=self.DEFAULT_LABEL
        )

        self.assertAlmostEqual(
            label.modified_at.timestamp(),
            timezone.now().timestamp(),
            delta=0.25
        )

        label.label = self.DEFAULT_LABEL + " Update"
        label.save()

        self.assertLessEqual(label.created_at, label.modified_at)

    def test_primary_key_is_uuid_and_unique(self):
        label1 = Label.objects.create(
            owner=self.user,
            label=self.DEFAULT_LABEL + " 1"
        )

        label2 = Label.objects.create(
            owner=self.user,
            label=self.DEFAULT_LABEL + " 2"
        )

        self.assertIsInstance(label1.id, uuid.UUID)
        self.assertIsInstance(label2.id, uuid.UUID)
        self.assertNotEqual(label1.id, label2.id)

    def test_unique_label_per_owner_constraint(self):
        label1 = Label.objects.create(
            owner=self.user,
            label=self.DEFAULT_LABEL + " Duplicate"
        )

        with self.assertRaises(Exception):
            Label.objects.create(owner=self.user, label=label1.label)
