# Generated by Django 4.2.16 on 2024-12-15 05:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_savedproduct'),
    ]

    operations = [
        migrations.RenameField(
            model_name='savedproduct',
            old_name='user_id',
            new_name='user',
        ),
    ]
