# Generated by Django 4.2.17 on 2025-01-22 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='custom_id',
            field=models.CharField(blank=True, max_length=8, null=True, unique=True),
        ),
    ]
