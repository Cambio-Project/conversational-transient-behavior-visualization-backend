from django.urls import path

from . import views

urlpatterns = [
    path('', views.dialogflow, name="dialogflow"),
]