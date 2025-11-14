import uuid
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from api.models import Collection

User = get_user_model()


class TestCollectionModel(TestCase):
    DEFAULT_COLLECTION_NAME = "Test Collection"

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_collection_owner",
            password="test_password",
            full_name="Test Collection Owner"
        )

    def test_collection_creation(self):
        collection = Collection.objects.create(
            owner=self.user,
            name=self.DEFAULT_COLLECTION_NAME
        )

        self.assertIsInstance(collection.id, uuid.UUID)
        self.assertEqual(collection.name, self.DEFAULT_COLLECTION_NAME)
        self.assertEqual(collection.owner, self.user)
        self.assertFalse(collection.is_default)
        self.assertIsNotNone(collection.created_at)
        self.assertIsNotNone(collection.updated_at)

    def test_str_representation(self):
        collection = Collection.objects.create(
            owner=self.user,
            name=self.DEFAULT_COLLECTION_NAME
        )

        expected = f"{collection.name} ({self.user.username})"
        self.assertEqual(str(collection), expected)

    def test_auto_timestamps(self):
        collection = Collection.objects.create(
            owner=self.user,
            name=self.DEFAULT_COLLECTION_NAME
        )

        self.assertAlmostEqual(
            collection.updated_at.timestamp(),
            timezone.now().timestamp(),
            delta=0.25
        )

        collection.name = self.DEFAULT_COLLECTION_NAME + " Updated"
        collection.save()

        self.assertLessEqual(collection.created_at, collection.updated_at)

    def test_primary_key_is_uuid_and_unique(self):
        c1 = Collection.objects.create(
            owner=self.user,
            name=self.DEFAULT_COLLECTION_NAME + " 1"
        )
        c2 = Collection.objects.create(
            owner=self.user,
            name=self.DEFAULT_COLLECTION_NAME + " 2"
        )

        self.assertIsInstance(c1.id, uuid.UUID)
        self.assertIsInstance(c2.id, uuid.UUID)
        self.assertNotEqual(c1.id, c2.id)

    def test_default_collection_uniqueness_per_owner(self):
        with self.assertRaises(ValidationError):
            Collection.objects.create(
                owner=self.user,
                name="Another Default Collection",
                is_default=True
            )

    def test_prevent_updating_non_default_to_default(self):
        c = Collection.objects.create(
            owner=self.user,
            name=self.DEFAULT_COLLECTION_NAME
        )
        c.is_default = True

        with self.assertRaises(ValidationError):
            c.save()

    def test_prevent_deleting_default_collection(self):
        default_col = self.user.collections.filter(is_default=True).first()

        with self.assertRaises(ValidationError):
            default_col.delete()

    def test_label_association(self):
        label = "cat"

        collection = Collection.objects.create(
            owner=self.user,
            name=self.DEFAULT_COLLECTION_NAME
        )

        collection.labels.append(label)
        self.assertIn(label, collection.labels)

    def test_duplicate_label_raises_exception(self):
        collection = Collection(
            owner=self.user,
            name="Test Collection",
            labels=["cat", "cat"],
        )

        with self.assertRaises(ValidationError):
            collection.save()
