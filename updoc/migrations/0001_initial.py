# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('value', models.CharField(db_index=True, max_length=255, verbose_name='keyword')),
            ],
        ),
        migrations.CreateModel(
            name='LastDocs',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('count', models.IntegerField(db_index=True, blank=True, default=1)),
                ('last', models.DateTimeField(db_index=True, auto_now=True, verbose_name='last')),
            ],
        ),
        migrations.CreateModel(
            name='ProxyfiedHost',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('host', models.CharField(db_index=True, help_text='Can be a regexp on URL (like http://*.example.com:*/*) or a subnet (like 192.168.0.0/24). Leave it blank to use as default value.',
                                          default='', blank=True, max_length=255, verbose_name='URL to proxify')),
                ('proxy', models.CharField(db_index=True, help_text='e.g. proxy.example.com:8080. Leave it empty if direct connexion. Several values can be given, separated by semi-colons (;).',
                                           default='', blank=True, max_length=255, verbose_name='Proxy to use')),
                ('priority', models.IntegerField(db_index=True, help_text='Low priorities are written first in proxy.pac', blank=True, default=0, verbose_name='Priority')),
            ],
            options={
                'verbose_name': 'Proxyfied host',
                'verbose_name_plural': 'Proxified hosts',
            },
        ),
        migrations.CreateModel(
            name='RewrittenUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('src', models.CharField(db_index=True, max_length=255, verbose_name='Original URL')),
                ('dst', models.CharField(db_index=True, blank=True, default='', max_length=255, verbose_name='New URL')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Rewritten URL',
                'verbose_name_plural': 'Rewritten URLs',
            },
        ),
        migrations.CreateModel(
            name='RssItem',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='name')),
                ('url', models.URLField(db_index=True, max_length=255, verbose_name='URL')),
            ],
            options={
                'verbose_name': 'element',
                'verbose_name_plural': 'elements',
            },
        ),
        migrations.CreateModel(
            name='RssRoot',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=255, verbose_name='name')),
            ],
            options={
                'verbose_name': 'favorite group',
                'verbose_name_plural': 'favorite groups',
            },
        ),
        migrations.CreateModel(
            name='UploadDoc',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('uid', models.CharField(db_index=True, max_length=50, verbose_name='uid')),
                ('name', models.CharField(db_index=True, default='', max_length=255, verbose_name='title')),
                ('path', models.CharField(db_index=True, max_length=255, verbose_name='path')),
                ('upload_time', models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='upload time')),
                ('keywords', models.ManyToManyField(db_index=True, to='updoc.Keyword', blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'documentation',
                'verbose_name_plural': 'documentations',
            },
        ),
        migrations.AddField(
            model_name='rssitem',
            name='root',
            field=models.ForeignKey(to='updoc.RssRoot', verbose_name='root'),
        ),
        migrations.AddField(
            model_name='lastdocs',
            name='doc',
            field=models.ForeignKey(to='updoc.UploadDoc'),
        ),
        migrations.AddField(
            model_name='lastdocs',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
    ]
