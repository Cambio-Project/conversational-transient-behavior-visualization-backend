from django.contrib import admin
from .models import Service
from .models import Dependency

# Register your models here.
admin.site.register(Service)
admin.site.register(Dependency)
