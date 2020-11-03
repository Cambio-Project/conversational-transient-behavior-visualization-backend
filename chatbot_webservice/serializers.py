from rest_framework import serializers

from .models import Service, Dependency, ServiceData, Specification


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'system', 'scenario', 'name', 'endpoints', 'violation_detected')


class DependencySerializer(serializers.HyperlinkedModelSerializer):
    source = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    target = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = Dependency
        fields = ('source', 'target', 'system')


class ServiceDataSerializer(serializers.HyperlinkedModelSerializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = ServiceData
        fields = ('service', 'time', 'callId', 'uri', 'qos', 'failureLoss', 'deploymentLoss', 'loadBalancingLoss')


class SpecificationSerializer(serializers.HyperlinkedModelSerializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = Specification
        fields = ('id', 'service', 'cause', 'max_initial_loss', 'max_recovery_time', 'max_lor')
