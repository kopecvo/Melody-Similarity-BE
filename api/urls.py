from django.urls import path

from . import views

urlpatterns = [
    path('search/', views.SearchView.as_view()),
    path('upload/', views.UploadMIDIView.as_view()),
]