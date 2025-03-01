# Generated by Django 4.2.16 on 2024-12-05 02:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0002_rename_user_testuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInput',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('routine_steps', models.IntegerField(max_length=10)),
                ('age', models.CharField(max_length=50)),
                ('skin_type', models.CharField(max_length=100)),
                ('skin_concerns', models.JSONField()),
                ('soothing_adj', models.JSONField()),
                ('sun_care_adj', models.JSONField()),
                ('well_aging_adj', models.JSONField()),
                ('acne', models.FloatField()),
                ('blackheads', models.FloatField()),
                ('brightening', models.FloatField()),
                ('sun_care', models.FloatField()),
                ('moisturising', models.FloatField()),
                ('dullness', models.FloatField()),
                ('soothing', models.FloatField()),
                ('stress', models.FloatField()),
                ('visible_pores', models.FloatField()),
                ('well_aging', models.FloatField()),
                ('sculpting', models.FloatField()),
                ('puffiness', models.FloatField()),
                ('scarring', models.FloatField()),
                ('dry', models.FloatField()),
                ('combination', models.FloatField()),
                ('oily', models.FloatField()),
                ('sensitive', models.FloatField()),
                ('normal', models.FloatField()),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
