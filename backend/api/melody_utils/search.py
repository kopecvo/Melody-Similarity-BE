from ..models import Song
import time
import numpy as np


def longest_substring(a, b):
    """
    Return length of longest substrings
    """

    m = len(a)
    n = len(b)

    arr = np.zeros(shape=[m + 1, n + 1], dtype='int')
    longest = 0

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                arr[i][j] = 0

            elif a[i - 1] == b[j - 1]:
                arr[i][j] = arr[i - 1][j - 1] + 1
                longest = max(longest, arr[i][j])

            else:
                arr[i][j] = 0

    return longest


def lookup(query):
    t = time.process_time()
    # Retrieve all songs from db
    songs = Song.objects.all()

    results = []

    for song in songs:
        song_notes = list(map(int, song.note_sequence.split(',')))
        res = longest_substring(song_notes, query)
        results.append((res, song))

    # Sort in descending order by the longest subsequence length
    results.sort(key=lambda tup: tup[0], reverse=True)
    t = time.process_time() - t
    print(f'Done in {t} seconds')
    return results
