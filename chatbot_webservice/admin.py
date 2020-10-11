from django.contrib import admin
from .models import Service, Dependency, ServiceData, Specification

# Register your models here.
admin.site.register(Service)
admin.site.register(Dependency)
admin.site.register(ServiceData)
admin.site.register(Specification)