from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .melody_utils.search import lookup
from .melody_utils.extractor import get_highest_melody
from api.forms import UploadFileForm
import os


uploadLocation = './upload/'

class SearchMelodyView(APIView):
    """
    A view that matches input melody with musical pieces in database
    """
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        if 'inputMelody' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            input_melody = request.data['inputMelody']
        except AttributeError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        res = lookup(input_melody)
        return Response(
            {
                'bestResultTitle': res[0][1].title,
                'author': res[0][1].author,
                'longestSubsequence': res[0][0]
            }
        )


class UploadMIDIView(APIView):
    """
    To upload custom MIDI files. Returns name of file if upload was successful, so it can be used
    to send another Query request specifying the filename
    """
    def post(self, request, format=None):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filename = uploadLocation + request.FILES['file'].name
            # Make upload folder if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # Write file
            with open(filename, 'wb+') as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)
            return Response({
                'filename': request.FILES['file'].name
            })

        return Response(status=status.HTTP_400_BAD_REQUEST)


class SearchMidiView(APIView):
    """
    A view that searches currently uploaded midi file
    """
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        if 'requestedMidi' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            filename = uploadLocation + request.data['requestedMidi']
            with open(filename, "r") as f:
                pass
        except OSError:
            os.remove(filename)
            return Response({
                'error': 'Requested file could not be opened'
            }, status=status.HTTP_400_BAD_REQUEST)

        f.close()
        # Try to extract first track
        extracted_melody = get_highest_melody(filename, [0], 5, True)

        if len(extracted_melody) > 40:
            os.remove(filename)
            return Response({
                'error': 'Melody in Midi is too long (> 40). Upload a shorter Midi'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(extracted_melody) < 4:
            os.remove(filename)
            return Response({
                'error': 'Melody in Midi is too short (< 4). Upload a longer Midi',
                'melodyLength': len(extracted_melody)
            }, status=status.HTTP_400_BAD_REQUEST)

        res = lookup(extracted_melody)
        os.remove(filename)
        return Response(
            {
                'bestResultTitle': res[0][1].title,
                'author': res[0][1].author,
                'longestSubsequence': res[0][0]
            }
        )
