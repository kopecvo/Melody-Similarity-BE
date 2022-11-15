from django.urls import path

from . import views

urlpatterns = [
    path('', views.QueryView.as_view()),
    path('extract', views.ExtractMelodyView.as_view()),
]