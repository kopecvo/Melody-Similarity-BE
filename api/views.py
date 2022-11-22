from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .melody_utils.search import lookup
from api.forms import UploadFileForm
import os


class SearchView(APIView):
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
            filename = './upload/' + request.FILES['file'].name
            # Make upload folder if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # Write file
            with open(filename, 'wb+') as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)
