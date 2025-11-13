from datetime import datetime, timezone, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import Image, Collection, Label
from api.serializers.image import ImageSerializer

User = get_user_model()


class TestImageSerializer(TestCase):
    DEFAULT_USERNAME = "image_owner"
    DEFAULT_PASSWORD = "test_password"
    DEFAULT_FULL_NAME = "Image Owner"
    DEFAULT_COLLECTION_NAME = "Test Collection"
    DEFAULT_FILENAME = "filename.jpg"
    DEFAULT_MIME_TYPE = "image/jpeg"
    DEFAULT_SIZE_BYTES = 1024

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

        self.valid_data = {
            "filename": self.DEFAULT_FILENAME,
            "mime_type": self.DEFAULT_MIME_TYPE,
            "size_bytes": self.DEFAULT_SIZE_BYTES,
            "collection": self.collection.id,
            "label_ids": [self.label.id],
        }

    def test_valid_serialization_and_creation(self):
        serializer = ImageSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        image = serializer.save()
        self.assertIsInstance(image, Image)
        self.assertEqual(image.owner, self.user)
        self.assertEqual(image.collection, self.collection)
        self.assertEqual(image.filename, self.DEFAULT_FILENAME)
        self.assertEqual(image.mime_type, self.DEFAULT_MIME_TYPE)
        self.assertEqual(image.size_bytes, self.DEFAULT_SIZE_BYTES)
        self.assertIn(self.label, image.labels.all())

    def test_read_only_fields_ignored_on_input(self):
        now = datetime.now(timezone.utc)
        data_with_readonly = {
            **self.valid_data,
            "id": "id",
            "created_at": (now - timedelta(days=1)).isoformat(),
            "updated_at": now.isoformat(),
        }

        serializer = ImageSerializer(data=data_with_readonly)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        image = serializer.save()

        self.assertNotEqual(str(image.id), "id")
        self.assertNotEqual(image.created_at.isoformat(), data_with_readonly["created_at"])
        self.assertNotEqual(image.updated_at.isoformat(), data_with_readonly["updated_at"])

    def test_missing_required_fields(self):
        invalid_data = {
            "owner": self.user.id,
            "collection": self.collection.id,
        }
        serializer = ImageSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("filename", serializer.errors)
        self.assertIn("mime_type", serializer.errors)
        self.assertIn("size_bytes", serializer.errors)

    def test_duplicate_label_association_allowed(self):
        serializer = ImageSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        image = serializer.save()

        image.labels.add(self.label)
        self.assertIn(self.label, image.labels.all())

    def test_serialized_output_contains_expected_fields(self):
        image = Image.objects.create(
            collection=self.collection,
            filename="output_image.jpg",
            mime_type=self.DEFAULT_MIME_TYPE,
            size_bytes=self.DEFAULT_SIZE_BYTES,
        )
        image.labels.add(self.label)

        serializer = ImageSerializer(image)
        data = serializer.data

        expected_fields = {
            "id",
            "filename",
            "mime_type",
            "size_bytes",
            "owner",
            "collection",
            "labels",
            "created_at",
            "updated_at",
        }

        self.assertTrue(expected_fields.issubset(data.keys()))
        self.assertEqual(data["filename"], image.filename)
        self.assertEqual(data["mime_type"], self.DEFAULT_MIME_TYPE)
        self.assertEqual(data["owner"], self.user.id)
        self.assertEqual(data["collection"], self.collection.id)
        self.assertEqual(len(data["labels"]), 1)
        self.assertEqual(data["labels"][0]["label"], self.label.label)
