import uuid
from typing import Optional

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from api.models import Image, Collection, Label

User = get_user_model()


class TestImageModel(TestCase):
    DEFAULT_FILENAME = "filename.jpg"
    DEFAULT_MIME_TYPE = "image/jpeg"
    DEFAULT_SIZE_BYTES = 1024

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_image_owner",
            password="test_password",
            full_name="Test Image Owner"
        )
        self.collection = Collection.objects.create(
            owner=self.user,
            name="Test Image Collection"
        )

    def _create_image(self, filename: Optional[str] = None):
        if filename is None:
            filename = self.DEFAULT_FILENAME

        image = Image.objects.create(
            collection=self.collection,
            filename=filename,
            mime_type=self.DEFAULT_MIME_TYPE,
            size_bytes=self.DEFAULT_SIZE_BYTES
        )

        return image

    def test_image_creation_and_filename_pattern(self):
        image = self._create_image()
        self.assertIsInstance(image.id, uuid.UUID)
        self.assertEqual(image.owner, self.user)
        self.assertEqual(image.collection, self.collection)
        self.assertEqual(image.filename, self.DEFAULT_FILENAME)
        self.assertEqual(image.mime_type, self.DEFAULT_MIME_TYPE)
        self.assertEqual(image.size_bytes, self.DEFAULT_SIZE_BYTES)
        self.assertIsNotNone(image.created_at)
        self.assertIsNotNone(image.updated_at)

    def test_str_representation(self):
        image = self._create_image()
        expected = f"{image.filename} ({self.user.username})"
        self.assertEqual(str(image), expected)

    def test_auto_timestamps(self):
        image = self._create_image()

        self.assertAlmostEqual(
            image.updated_at.timestamp(),
            timezone.now().timestamp(),
            delta=0.25
        )

        image.size_bytes += 100
        image.save()

        self.assertLessEqual(image.created_at, image.updated_at)

    def test_primary_key_is_uuid_and_unique(self):
        filename1 = "(1) " + self.DEFAULT_FILENAME
        filename2 = "(2) " + self.DEFAULT_FILENAME

        image1 = self._create_image(filename1)
        image2 = self._create_image(filename2)

        self.assertIsInstance(image1.id, uuid.UUID)
        self.assertIsInstance(image2.id, uuid.UUID)
        self.assertNotEqual(image1.id, image2.id)
        self.assertNotEqual(image1.stored_filename, image2.stored_filename)
        self.assertEqual(image1.filename, filename1)
        self.assertEqual(image2.filename, filename2)

    def test_label_association(self):
        label = Label.objects.create(
            owner=self.user,
            label="Test Image Label"
        )

        image = self._create_image("labeled_image.jpeg")
        image.labels.add(label)

        self.assertIn(label, image.labels.all())
        self.assertIn(image, label.images.all())

    def test_owner_is_auto_generated(self):
        dummy_user = User.objects.create_user(
            username="dummy_user",
            password="test_password",
            full_name="Dummy User"
        )

        image = Image.objects.create(
            collection=self.collection,
            owner=dummy_user,
            filename="file.jpg",
            mime_type="image/jpeg",
            size_bytes=500,
        )

        image.refresh_from_db()

        self.assertEqual(image.owner, self.user)
        self.assertNotEqual(image.owner, dummy_user)

    def test_stored_filename_is_auto_generated(self):
        image = Image.objects.create(
            collection=self.collection,
            stored_filename="name.jpg",
            filename="file.jpg",
            mime_type="image/jpeg",
            size_bytes=500,
        )

        image.refresh_from_db()

        expected_stored = f"{image.id}.jpeg"

        self.assertEqual(image.stored_filename, expected_stored)
        self.assertNotEqual(image.stored_filename, "name.jpg")
