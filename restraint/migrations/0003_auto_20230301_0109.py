# Generated by Django 3.2.16 on 2023-03-01 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restraint', '0002_permset_is_private'),
    ]

    operations = [
        migrations.AddField(
            model_name='perm',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='perm',
            name='is_locked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='permset',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='permset',
            name='is_locked',
            field=models.BooleanField(default=False),
        ),
    ]
