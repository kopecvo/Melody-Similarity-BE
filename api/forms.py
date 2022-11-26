from django import forms


class UploadFileForm(forms.Form):
    """A simple form to temporarily save Midi files, so melodies can be extracted from them"""
    file = forms.FileField()
