import time
from hashlib import md5

from django.contrib.auth.models import AbstractUser
from django.contrib.staticfiles.templatetags.staticfiles import static
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

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return static("ui/user.png")
