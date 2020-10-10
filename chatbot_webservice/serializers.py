from rest_framework import serializers

from .models import Service, Dependency


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name')


class DependencySerializer(serializers.HyperlinkedModelSerializer):
    source = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    target = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = Dependency
        fields = ('source', 'target')
