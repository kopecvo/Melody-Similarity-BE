from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.melody_utils.search import search_lcs, search_dtw
from api.melody_utils.extractor import get_highest_melody
from api.forms import UploadFileForm
from api.models import DTWResultGraph
import os
import uuid


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

        results = []
        # Search with LCS
        if request.data['searchFn'] == "lcs":
            res = search_lcs(input_melody)
            for i in range(request.data['numOfResults']):
                results.append({
                    'title': res[i]['song'].title,
                    'author': res[i]['song'].author,
                    'lcs': res[i]['lcs'],
                    'segment': res[i]['segment'],
                    'segmentMelody': res[i]['segment_melody'],
                    'truthArray': res[i]['truth_array']
                })

        # Search with DTW
        elif request.data['searchFn'] == "dtw":
            res = search_dtw(input_melody, request.data['numOfResults'])
            for i in range(request.data['numOfResults']):
                results.append({
                    'title': res[i]['song'].title,
                    'author': res[i]['song'].author,
                    'dtwDistance': res[i]['distance'],
                    'segment': res[i]['segment'],
                    'segmentMelody': res[i]['segment_melody'],
                    'graphUrl': DTWResultGraph.objects.filter(result_index=i)[0].graph.url
                })

        return Response(
            {
                'searchFn': request.data['searchFn'],
                'results': results
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
            # Make a safe filename
            filename = uploadLocation + str(uuid.uuid4())
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
                    'error': 'Melody in Midi is too long (> 40). Extracted first 40 notes',
                    'melody': extracted_melody[0:40]
                })

            if len(extracted_melody) == 0:
                os.remove(filename)
                return Response({
                    'error': 'Extracted 0 notes. Midi file is empty',
                    'melody': extracted_melody
                })

            os.remove(filename)
            return Response({
                'melody': extracted_melody
            })

        return Response(status=status.HTTP_400_BAD_REQUEST)
