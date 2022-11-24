from django.urls import path

from . import views

urlpatterns = [
    path('extract/', views.ExtractMelodyFromMidiView.as_view()),
    path('search/', views.SearchMelodyView.as_view()),
]