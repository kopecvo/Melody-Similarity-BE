from django.db import models

# Create your models here.
class Melody(models.Model):
    note_sequence = models.IntegerField(default=0)
    note_delta_sequence = models.IntegerField(default=0)
    filename = models.CharField(max_length=60)