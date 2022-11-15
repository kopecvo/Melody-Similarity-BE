from django.urls import path

from . import views

urlpatterns = [
    path('', views.QueryView.as_view()),
]