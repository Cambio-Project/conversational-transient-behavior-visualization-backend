from rest_framework import serializers

from .models import Service, Dependency, ServiceData


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


class ServiceDataSerializer(serializers.HyperlinkedModelSerializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = ServiceData
        fields = ('service', 'time', 'callId', 'uri', 'successfulTransactions', 'failedTransactions', 'droppedTransactions',
                  'avgResponseTime')
