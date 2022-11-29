from rest_framework import serializers
from api.models import Song


class SongSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=60)
    author = serializers.CharField(max_length=60)
    filename = serializers.CharField(max_length=100)
    note_sequence = serializers.CharField()
    note_delta_sequence = serializers.CharField()

    def create(self, validated_data):
        """
        Create and return a new `Song` instance, given the validated data.
        """
        return Song.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Song` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.author = validated_data.get('author', instance.author)
        instance.filename = validated_data.get('filename', instance.filename)
        instance.note_sequence = validated_data.get('note_sequence', instance.note_sequence)
        instance.note_delta_sequence = validated_data.get('note_delta_sequence', instance.note_delta_sequence)
        instance.save()
        return instance
