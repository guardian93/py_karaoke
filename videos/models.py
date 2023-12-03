from django.db import models


class Video(models.Model):
    video_id = models.CharField(max_length=10)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    thumbnail_url = models.CharField(max_length=100)
    status = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.title}: {self.description}'


class Controller(models.Model):
    attribute = models.CharField(max_length=30, primary_key=True)
    value = models.IntegerField()
