from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'services', views.ServiceViewSet, basename='service')
router.register(r'dependencies', views.DependencyViewSet, basename='dependency')
router.register(r'servicedata', views.ServiceDataViewSet, basename='servicedata')
router.register(r'specifications', views.SpecificationViewSet, basename='specification')

urlpatterns = [
    path('dialogflow/', views.dialogflow, name='dialogflow'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
