# Generated by Django 3.1.7 on 2021-04-05 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0002_channel_welcome_msg'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='redirect_url',
            field=models.CharField(default='/', max_length=255),
        ),
    ]
