# Generated by Django 2.2.4 on 2019-08-31 09:33

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20190831_0734'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, upload_to=users.models.user_photo_path),
        ),
    ]
