from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


class QueryView(APIView):
    """
    A view that matches input melody with musical pieces in database
    """
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        if 'input_melody' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            input_melody = request.data['input_melody'].split(',')
        except AttributeError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        print(input_melody)
        return Response({'input melody': input_melody})

