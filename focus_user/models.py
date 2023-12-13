# from https://www.youtube.com/watch?v=kRJpQxi2jIo
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import int_list_validator

import os

class FocusUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=1000, default='')
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')

    def __str__(self) -> str:
        return self.user.username

class Upload(models.Model):
    title = models.CharField(max_length=255)
    caption = models.CharField(max_length=1000)
    category = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/')
    average_rating = models.FloatField()
    total_ratings = models.IntegerField()
    upload_user = models.ForeignKey(FocusUser, on_delete=models.CASCADE, related_name='uploads')
    raters = models.ManyToManyField(FocusUser, symmetrical=False, related_name='rated_uploads')

    def delete(self, *args, **kwargs):
        # Delete the associated image file before calling the parent delete method
        storage, path = self.image.storage, self.image.path
        if os.path.isfile(path):
            storage.delete(path)

        # Call the parent delete method to delete the model instance from the database
        super(Upload, self).delete(*args, **kwargs)

class Comment(models.Model):
    comment = models.CharField(max_length=5000)
    upload = models.ForeignKey(Upload, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(FocusUser, on_delete=models.CASCADE, related_name='comments')
