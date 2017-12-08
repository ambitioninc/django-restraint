# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Perm',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=256, blank=True)),
                ('display_name', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PermAccess',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('perm_user_id', models.PositiveIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PermLevel',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=256, blank=True)),
                ('display_name', models.TextField(blank=True)),
                ('perm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restraint.Perm')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PermSet',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=256, blank=True)),
                ('display_name', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='permlevel',
            unique_together=set([('perm', 'name')]),
        ),
        migrations.AddField(
            model_name='permaccess',
            name='perm_levels',
            field=models.ManyToManyField(to='restraint.PermLevel'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='permaccess',
            name='perm_set',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, default=None, null=True, to='restraint.PermSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='permaccess',
            name='perm_user_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, default=None, null=True, to='contenttypes.ContentType'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='permaccess',
            unique_together=set([('perm_user_type', 'perm_user_id')]),
        ),
    ]
