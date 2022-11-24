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


class ExtractMelodyFromMidiView(APIView):
    """
    Upload a Midi file and try to extract melody from it. Return extracted melody
    All midi tracks are used
    """
    def post(self, request, format=None):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filename = uploadLocation + request.FILES['file'].name
            # Make upload folder if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # Save file temporarily so extraction functions can access it
            with open(filename, 'wb+') as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)

            # Try to extract melody. Merge all tracks
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

            os.remove(filename)
            return Response({
                'melody': extracted_melody
            })

        return Response(status=status.HTTP_400_BAD_REQUEST)
