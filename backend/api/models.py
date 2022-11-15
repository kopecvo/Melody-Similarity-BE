from django.db import models


# Create your models here.
class Song(models.Model):
    title = models.CharField(max_length=60)
    author = models.CharField(max_length=60)
    filename = models.CharField(max_length=100)
    note_sequence = models.TextField()
    note_delta_sequence = models.TextField()
