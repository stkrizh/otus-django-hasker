# Generated by Django 2.2.4 on 2019-09-11 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0008_auto_20190911_0715'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='number_of_answers',
            field=models.IntegerField(default=0),
        ),
    ]
