import numpy as np
from mido import MidiFile
from collections import namedtuple

TimedNote = namedtuple('TimedNote', ['note', 'start_tick', 'end_tick'])
CustomMessage = namedtuple('CustomMessage', ['start_tick', 'note', 'on'])


class ActiveNotes:
    """Structure for keeping track of all notes playing at the same time while iterating through a song"""

    def __init__(self):
        self.cur_tick = 0
        self.currently_playing = np.zeros([128], dtype='bool')
        # Array to prevent adding the same highest note twice
        # (f.e. some note gets turned off and some note which has been added to the melody already
        # might still be playing and gets evaluated as highest note again)
        self.already_in_melody = np.zeros([128], dtype='bool')

    def note_on(self, note):
        self.currently_playing[note] = True

    def note_off(self, note):
        self.currently_playing[note] = False
        self.already_in_melody[note] = False

    def get_highest_note(self, delta_tick):
        """
        Return highest note and ticks when it started/stopped

        :param delta_tick: time (in ticks) since latest MIDI Message
        """
        previous_tick = self.cur_tick
        self.cur_tick = self.cur_tick + delta_tick
        for i in range(127, -1, -1):
            # Found the highest note that's currently playing
            if self.currently_playing[i]:
                # It hasn't been added to melody yet; add it
                if not self.already_in_melody[i]:
                    self.already_in_melody[i] = True
                    return TimedNote(i, previous_tick, self.cur_tick)

                # Has been added to melody; stop the search for highest note
                else:
                    break

        return TimedNote(-1, previous_tick, self.cur_tick)


def get_highest_melody(file, tracks_to_merge, tick_ignore):
    """
    Get the highest melody from a MIDI file.

    :param file: path to MIDI file
    :param tracks_to_merge: list of indexes of tracks that will be merged and inspected for melody
    :param tick_ignore: if tick difference between two notes is smaller than this value, interpret the notes
        as being played simultaneously (useful for spread-out chords, etc.)
    """
    mid = MidiFile(file)
    highest_melodies = []
    merged_melody = []

    # Process all tracks separately first - get each track's highest melody
    for track_no in tracks_to_merge:
        an = ActiveNotes()
        highest_melody = []
        additive_tick = 0
        for msg in mid.tracks[track_no]:
            if msg.type == 'note_on':
                tick = msg.time + additive_tick
                additive_tick = 0
                # Not instant; some time has passed => evaluate previous highest note
                if tick != 0:
                    res = an.get_highest_note(tick)
                    # Filter out cases when nothing is playing
                    if res.note != -1:
                        # highest_melody.append(res)
                        # Add turn on/turn off messages
                        highest_melody.append(CustomMessage(res.start_tick, res.note, 1))
                        highest_melody.append(CustomMessage(res.end_tick, res.note, 0))

                if msg.velocity != 0:
                    an.note_on(msg.note)
                else:
                    an.note_off(msg.note)

            # Some messages change tick ('set_tempo', 'control_change', 'time_signature', ...)
            # The tick from these accumulates and will be added to the next 'note_on' message
            else:
                additive_tick = additive_tick + msg.time

        highest_melodies.append(highest_melody)

    # Merge all highest melody messages into one list
    mega_list = []
    for i in highest_melodies:
        mega_list = mega_list + i

    # Sort all messages by starting tick
    mega_list.sort(key=lambda custom_msg: custom_msg.start_tick)
    an = ActiveNotes()
    cur_tick = mega_list[0][0]

    for custom_msg in mega_list:
        # Treat a very small time difference between messages as if the events happened simultaneously
        # So that the higher note gets judged correctly
        if abs(custom_msg.start_tick - cur_tick) > tick_ignore:
            res = an.get_highest_note(0)
            if res.note != -1:
                merged_melody.append(res.note)

        if custom_msg.on:
            an.note_on(custom_msg.note)

        else:
            an.note_off(custom_msg.note)

        cur_tick = custom_msg.start_tick

    return merged_melody
