# Generated by Django 5.0 on 2023-12-12 06:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('focus_user', '0002_focususer_bio_focususer_followers_upload'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=5000)),
                ('upload', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='focus_user.upload')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='focus_user.focususer')),
            ],
        ),
    ]