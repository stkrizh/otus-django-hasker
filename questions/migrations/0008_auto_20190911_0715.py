# Generated by Django 2.2.4 on 2019-09-11 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0007_postgres_trigram'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='number_of_votes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='question',
            name='number_of_votes',
            field=models.IntegerField(default=0),
        ),
    ]
