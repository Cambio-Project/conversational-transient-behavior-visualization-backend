from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'services', views.ServiceViewSet)
router.register(r'dependencies', views.DependencyViewSet)

urlpatterns = [
    path('dialogflow/', views.dialogflow, name='dialogflow'),
    # path('api/services/', views.services, name="services"),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
