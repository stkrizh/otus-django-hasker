import time
from hashlib import md5

from PIL import Image

from django.contrib.auth.models import AbstractUser
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models


def user_photo_path(instance, filename):
    name, sep, ext = filename.rpartition(".")
    if not sep:
        ext = ".jpg"

    new_filename = md5(str(time.time()).encode("utf-8")).hexdigest()
    return f"userpics/{new_filename}.{ext}"


class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    photo = models.ImageField(blank=True, upload_to=user_photo_path)
    thumb = models.ImageField(
        blank=True, editable=False, upload_to=user_photo_path
    )

    def save(self, *args, **kwargs):
        if self.photo and self._state.adding:
            self.create_thumbnail()
        super().save(*args, **kwargs)

    def create_thumbnail(self, save=False):
        content = ContentFile(b"")
        with Image.open(self.photo) as img:
            img.thumbnail((150, 150))
            img.convert(mode="RGB").save(content, format="JPEG")

        self.thumb = InMemoryUploadedFile(
            content, None, "temp.jpg", "image/jpeg", len(content), None
        )
        if save:
            self.save(update_fields=["thumb"])

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return static("ui/user.png")

    def get_thumb_url(self):
        if self.thumb:
            return self.thumb.url
        return self.get_photo_url()
