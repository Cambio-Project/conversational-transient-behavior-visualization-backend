from django.urls import path

from . import views

urlpatterns = [
    path('dialogflow/', views.dialogflow, name='dialogflow'),
    path('api/services/', views.services, name='services'),
]
