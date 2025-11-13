from datetime import timedelta, datetime, timezone

from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import Collection, Label, Image
from api.serializers.collection import CollectionSerializer

User = get_user_model()


class TestCollectionSerializer(TestCase):
    DEFAULT_USERNAME = "serializer_collection_owner"
    DEFAULT_PASSWORD = "test_password"
    DEFAULT_FULL_NAME = "Serializer Collection Owner"
    DEFAULT_COLLECTION_NAME = "Serializer Test Collection"

    def setUp(self):
        self.user = User.objects.create_user(
            username=self.DEFAULT_USERNAME,
            password=self.DEFAULT_PASSWORD,
            full_name=self.DEFAULT_FULL_NAME,
        )
        self.collection = Collection.objects.create(
            owner=self.user,
            name=self.DEFAULT_COLLECTION_NAME,
        )

        self.label = Label.objects.create(owner=self.user, label="Serializer Label")
        self.image = Image.objects.create(
            collection=self.collection,
            filename="filename.jpg",
            mime_type="image/jpeg",
            size_bytes=1024,
        )

    def test_serialized_output_contains_expected_fields(self):
        serializer = CollectionSerializer(self.collection)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("name", data)
        self.assertIn("is_default", data)
        self.assertIn("owner", data)
        self.assertIn("labels", data)
        self.assertIn("images", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

        self.assertEqual(data["name"], self.DEFAULT_COLLECTION_NAME)
        self.assertEqual(data["owner"], self.user.id)
        self.assertFalse(data["is_default"])

    def test_valid_serialization_and_creation(self):
        valid_data = {
            "name": "New Collection",
            "owner": self.user.id,
            "label_ids": [self.label.id],
            "image_ids": [self.image.id],
        }

        serializer = CollectionSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        collection = serializer.save()
        self.assertIsInstance(collection, Collection)
        self.assertEqual(collection.name, valid_data["name"])
        self.assertEqual(collection.owner, self.user)
        self.assertIn(self.label, collection.labels.all())
        self.assertIn(self.image, collection.images.all())

    def test_read_only_fields_ignored_on_input(self):
        now = datetime.now(timezone.utc)
        data_with_readonly = {
            "name": "Collection Ignore Fields",
            "owner": self.user.id,
            "is_default": True,
            "created_at": (now - timedelta(days=1)).isoformat(),
            "updated_at": now.isoformat(),
        }

        serializer = CollectionSerializer(data=data_with_readonly)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        collection = serializer.save()

        self.assertFalse(collection.is_default)
        self.assertNotEqual(collection.created_at.isoformat(), data_with_readonly["created_at"])

    def test_missing_required_fields(self):
        invalid_data = {"owner": self.user.id}
        serializer = CollectionSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_label_and_image_relationships_are_read_only_on_output(self):
        self.collection.labels.add(self.label)
        self.collection.images.add(self.image)

        serializer = CollectionSerializer(self.collection)
        data = serializer.data

        self.assertEqual(len(data["labels"]), 1)
        self.assertEqual(len(data["images"]), 1)
        self.assertEqual(data["labels"][0]["label"], self.label.label)
        self.assertEqual(data["images"][0], self.image.id)

