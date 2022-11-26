from django.db import models


class Song(models.Model):
    """
    A model to store extracted melodies of songs, which are then compared during searching
    """
    title = models.CharField(max_length=60)
    author = models.CharField(max_length=60)
    filename = models.CharField(max_length=100)
    note_sequence = models.TextField()
    note_delta_sequence = models.TextField()


class DTWResultGraph(models.Model):
    """
    A model for temporarily storing generated graphs of DTW results
    We can then send the url of the images and serve them in frontend (until new search request is sent)
    """
    result_index = models.IntegerField()     # Index of the result the graph belongs to
    graph = models.ImageField()
