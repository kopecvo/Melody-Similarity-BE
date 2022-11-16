from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .melody_utils.search import lookup


class QueryView(APIView):
    """
    A view that matches input melody with musical pieces in database
    """
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        if 'input_melody' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            input_melody = request.data['input_melody']
        except AttributeError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        res = lookup(input_melody)
        return Response(
            {
                'best result title': res[0][1].title,
                'longest subsequence': res[0][0]
            }
        )

