# Generated by Django 5.0 on 2023-12-13 04:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('focus_user', '0005_upload_raters'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='user',
        ),
        migrations.RemoveField(
            model_name='focususer',
            name='followers',
        ),
        migrations.RemoveField(
            model_name='upload',
            name='raters',
        ),
        migrations.RemoveField(
            model_name='upload',
            name='upload_user',
        ),
    ]
