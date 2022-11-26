import time
import numpy as np
import math
import os
import shutil
import uuid
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from matplotlib import style
from pathlib import Path
from django.core.files import File
from api.models import DTWResultGraph, Song

temporary_graphs_folder = 'upload/graphs/'

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
    t = time.process_time() - t
    print(f'LCS done in {t} seconds.')
    return results


def search_dtw(query, num_of_results):
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

    generate_dtw_graphs(query, results, num_of_results)

    t = time.process_time() - t
    print(f'DTW done in {t} seconds.')
    return results


def generate_dtw_graph(query, dtw_result, result_index):
    """
    Generate a dtw graph using pyplot. Return path where image is saved
    """
    segment = dtw_result['segment_melody']
    segment_len = len(segment)

    plt.style.use('Solarize_Light2')

    # print(f'----{result_index}-----')
    # print(dtw_result['dtw_path'])

    for mapping in dtw_result['dtw_path']:
        x1 = mapping[0]
        y1 = segment[mapping[0]]
        x2 = mapping[1]
        y2 = query[mapping[1]]
        color = 'limegreen'
        plt.plot([x1, x2], [y1, y2], color=color, linestyle='-', linewidth=1)

    plt.plot(query, label='Search', linewidth=2)
    plt.plot(segment, label='Song', linewidth=2, color='orange')
    plt.locator_params(axis="both", integer=True, tight=True)
    plt.legend()

    # Get path to save image
    save_path = f'{temporary_graphs_folder}{str(uuid.uuid4())}.png'

    # Make upload folder if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    # Save image to path
    plt.savefig(save_path)
    # Clear plot
    plt.clf()

    return save_path


def generate_dtw_graphs(query, sorted_dtw_results, num_of_returned_results):
    # Delete stored files of previous results
    for old_graph in DTWResultGraph.objects.all():
        old_graph.graph.delete()

    # Delete old graph entries (this doesn't delete the file so we have to do it manually above)
    DTWResultGraph.objects.all().delete()

    for i in range(num_of_returned_results):
        dtw_graph = DTWResultGraph(result_index=i)
        dtw_graph_path = generate_dtw_graph(query, sorted_dtw_results[i], i)
        path = Path(dtw_graph_path)
        with path.open(mode='rb') as f:
            dtw_graph.graph = File(f, name=path.name)
            dtw_graph.save()

    # Delete temporary graphs folder
    shutil.rmtree(temporary_graphs_folder)
