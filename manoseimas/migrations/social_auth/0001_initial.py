# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from social.storage.django_orm import DjangoAssociationMixin
from social.storage.django_orm import DjangoUserMixin
from social.storage.django_orm import DjangoNonceMixin

from django.conf import settings
import social.apps.django_app.default.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Association',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('server_url', models.CharField(max_length=255)),
                ('handle', models.CharField(max_length=255)),
                ('secret', models.CharField(max_length=255)),
                ('issued', models.IntegerField(db_index=True)),
                ('lifetime', models.IntegerField()),
                ('assoc_type', models.CharField(max_length=64)),
            ],
            bases=(models.Model, DjangoAssociationMixin),
        ),
        migrations.CreateModel(
            name='Nonce',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('server_url', models.CharField(max_length=255)),
                ('timestamp', models.IntegerField(db_index=True)),
                ('salt', models.CharField(max_length=40)),
            ],
            bases=(models.Model, DjangoNonceMixin),
        ),
        migrations.CreateModel(
            name='UserSocialAuth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('provider', models.CharField(max_length=32)),
                ('uid', models.CharField(max_length=255)),
                ('extra_data', social.apps.django_app.default.fields.JSONField(default=b'{}')),
                ('user', models.ForeignKey(related_name='social_auth', to=settings.AUTH_USER_MODEL)),
            ],
            bases=(models.Model, DjangoUserMixin),
        ),
        migrations.AlterUniqueTogether(
            name='nonce',
            unique_together=set([('server_url', 'timestamp', 'salt')]),
        ),
        migrations.AlterUniqueTogether(
            name='association',
            unique_together=set([('server_url', 'handle')]),
        ),
        migrations.AlterUniqueTogether(
            name='usersocialauth',
            unique_together=set([('provider', 'uid')]),
        ),
    ]
