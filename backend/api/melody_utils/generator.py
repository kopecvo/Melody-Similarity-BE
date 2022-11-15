from ..models import Song
from .extractor import get_highest_melody
from mido import MidiFile
import os


def get_metadata_piano_midi_de(file):
    # Load a midi file
    mid = MidiFile(file)
    track_name = ""
    author = ""
    # First track contains data
    for msg in mid.tracks[0]:
        # Not instant; some time has passed => evaluate previous highest note
        if msg.type == "track_name":
            if track_name == "":
                track_name = msg.name
            else:
                track_name = track_name + ": " + msg.name

        # First text message contains the author
        if msg.type == "text":
            author = msg.text
            break

    # Second and third tracks contain right/left hand
    melody = get_highest_melody(file, [1, 2], 5)
    return {
        "track_name": track_name,
        "author": author,
        "file": file,
        "melody": melody
    }


def generate_all_piano_midi_de():
    """
    Generate melodies for all MIDI songs from www.piano-midi.de
    """
    relative_dir = "midi/piano_midi_de"
    directory = os.fsencode(relative_dir)

    for subdir, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.fsdecode(os.path.join(subdir, file))

            meta = get_metadata_piano_midi_de(full_path)
            song = Song(title=meta["track_name"],
                        author=meta["author"],
                        filename=meta["file"],
                        note_sequence=','.join(map(str, meta["melody"]))
                        )

            song.save()
            print(f'Generated song {full_path}')