from ..models import Song
import time
import numpy as np
import math
from fastdtw import fastdtw
import matplotlib.pyplot as plt


def lcs_get_string(segment, query):
    """Traverse LCS table and get LCS string"""
    m = len(segment)
    n = len(query)

    # Declaring the table for storing the dp values
    a = np.zeros(shape=[m + 1, n + 1], dtype='int')

    # LCS DP
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                a[i][j] = 0

            elif segment[i - 1] == query[j - 1]:
                a[i][j] = a[i - 1][j - 1] + 1

            else:
                a[i][j] = max(a[i - 1][j], a[i][j - 1])

    lcs_str = []

    # Start from the right-most-bottom-most corner and
    # one by one store characters in lcs[]
    i = m
    j = n
    while i > 0 and j > 0:

        # If current character in X[] and Y are same, then
        # current character is part of LCS
        if segment[i - 1] == query[j - 1]:
            lcs_str.append(segment[i - 1])
            i -= 1
            j -= 1

        # If not same, then find the larger of two and
        # go in the direction of larger value
        elif a[i - 1][j] > a[i][j - 1]:
            i -= 1

        else:
            j -= 1


    # We traversed the table in reverse order
    # LCS is the reverse of what we got
    lcs_str.reverse()
    return lcs_str


def lcs(segment, query):
    """Standard DP LCS implementation"""
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


def search_lcs(query):
    """For a query melody, try to match it to songs in db using LCS"""

    t = time.process_time()
    # Retrieve all songs from db
    songs = Song.objects.all()

    results = []
    query_len = len(query)

    for song in songs:
        song_notes = list(map(int, song.note_sequence.split(',')))
        
        song_len = len(song_notes)
        max_len = 0
        max_first_index = 0
        max_last_index = 0
        max_segment_melody = []

        # Split song into segments of length of query
        for i in range(math.ceil(song_len / query_len)):
            first_note_index = i * query_len
            last_note_index = (i + 1) * query_len   # (first one excluded)

            segment = song_notes[first_note_index:last_note_index]

            # Last note index can be out of range but array slicing is safe against that
            # Get segment with highest LCS
            res = lcs(segment, query)
            if res > max_len:
                max_len = res
                max_first_index = first_note_index
                max_last_index = last_note_index
                max_segment_melody = segment

        # Get LCS truth array for frontend
        truth_array = []
        lcs_iterator = 0
        lcs_string = lcs_get_string(max_segment_melody, query)

        for note in max_segment_melody:
            if lcs_iterator < max_len:
                if note == lcs_string[lcs_iterator]:
                    truth_array.append(True)
                    lcs_iterator += 1
                else:
                    truth_array.append(False)

            else:
                break

        results.append({
            'lcs_length': max_len,
            'song': song,
            'segment': [max_first_index, max_last_index - 1],
            'segment_melody': max_segment_melody,
            'lcs': lcs_string,
            'truth_array': truth_array
        })


    # Sort in descending order by LCS length
    results.sort(key=lambda res: res['lcs_length'], reverse=True)
    print(results[0]['lcs_length'])
    t = time.process_time() - t
    print(f'Done in {t} seconds')
    return results


def search_dtw(query):
    """For a query melody, try to match it to songs in db using DTW"""

    t = time.process_time()
    # Retrieve all songs from db
    songs = Song.objects.all()

    results = []
    query_len = len(query)

    for song in songs:
        song_notes = list(map(int, song.note_sequence.split(',')))
        song_len = len(song_notes)

        min_distance = np.inf
        min_first_index = 0
        min_last_index = 0
        min_path = []
        min_segment_melody = []

        # Get segments
        for i in range(math.ceil(song_len / query_len)):
            first_note_index = i * query_len
            last_note_index = (i + 1) * query_len

            segment = song_notes[first_note_index:last_note_index]

            # Last note index can be out of range but array slicing is safe against that
            distance, path = fastdtw(segment, query)
            if distance < min_distance:
                min_distance = distance
                min_first_index = first_note_index
                min_last_index = last_note_index
                min_path = path
                min_segment_melody = segment

        results.append({
            'distance': min_distance,
            'song': song,
            'segment': [min_first_index, min_last_index - 1],
            'segment_melody': min_segment_melody,
            'dtw_path': min_path
        })

    # Sort in ascending order by the smallest DTW distance
    results.sort(key=lambda res: res['distance'])
    t = time.process_time() - t
    print(f'Done in {t} seconds')
    return results
