from ..models import Song
import time
import numpy as np
import math


def longest_common_subsequence(segment, query):
    m = len(segment)
    n = len(query)

    # Declaring the table for storing the dp values
    a = np.zeros(shape=[m + 1, n + 1], dtype='int')

    # LCS DP
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                a[i][j] = 0

            elif segment[i-1] == query[j-1]:
                a[i][j] = a[i-1][j-1] + 1

            else:
                a[i][j] = max(a[i-1][j], a[i][j-1])

    return a[m][n]


# Break songs into segments of same length as query
def search(query):
    t = time.process_time()
    # Retrieve all songs from db
    songs = Song.objects.all()

    results = []
    query_len = len(query)

    for song in songs:
        song_notes = list(map(int, song.note_sequence.split(',')))
        
        song_len = len(song_notes)
        max_res = 0
        max_first_index = 0
        max_last_index = 0

        # Split song into segments of length of query
        for i in range(math.ceil(song_len / query_len)):
            first_note_index = i * query_len
            last_note_index = (i + 1) * query_len   # (first one excluded)

            # Last note index can be out of range but array slicing is safe against that
            # Get segment with highest LCS
            res = longest_common_subsequence(song_notes[first_note_index:last_note_index], query)
            if res > max_res:
                max_res = res
                max_first_index = first_note_index
                max_last_index = last_note_index

        results.append((max_res, song, [max_first_index, max_last_index]))

    # Sort in descending order by LCS
    results.sort(key=lambda tup: tup[0], reverse=True)
    t = time.process_time() - t
    print(f'Done in {t} seconds')
    return results

