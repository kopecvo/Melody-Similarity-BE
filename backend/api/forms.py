from django import forms


class QueryForm(forms.Form):
    query_sequence = forms.CharField()
