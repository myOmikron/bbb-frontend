# Generated by Django 3.1.7 on 2021-04-24 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0005_remove_channel_viewers'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='websocket_url',
            field=models.CharField(default='/', max_length=255),
        ),
    ]
