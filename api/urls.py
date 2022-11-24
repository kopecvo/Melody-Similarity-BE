from django.urls import path

from . import views

urlpatterns = [
    path('search/midi/', views.SearchMidiView.as_view()),
    path('search/melody/', views.SearchMelodyView.as_view()),
    path('upload/', views.UploadMIDIView.as_view()),
]