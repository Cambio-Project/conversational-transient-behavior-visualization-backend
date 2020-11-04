from django.db import models
from django.contrib.postgres.fields import ArrayField


class Service(models.Model):
    system = models.CharField(max_length=200)
    scenario = models.IntegerField(max_length=3)
    name = models.CharField(max_length=200, null=False, blank=False)
    endpoints = ArrayField(models.CharField(max_length=300), blank=True)
    violation_detected = models.BooleanField(default=False)

    def __str__(self):
        return str(f'{self.name}, Scenario: {self.scenario}')


class Dependency(models.Model):
    system = models.CharField(max_length=200)
    source = models.ForeignKey(Service, related_name='source', on_delete=models.CASCADE)
    target = models.ForeignKey(Service, related_name='target', on_delete=models.CASCADE)

    def __str__(self):
        return self.source.name + " -> " + self.target.name


class ServiceData(models.Model):
    service = models.ForeignKey(Service, related_name='service', on_delete=models.CASCADE)
    time = models.DecimalField(null=False, decimal_places=4, max_digits=10)
    callId = models.IntegerField(null=False)
    uri = models.CharField(max_length=300, null=False)
    qos = models.IntegerField(null=False)
    failureLoss = models.DecimalField(null=False, default=0.0000, decimal_places=4, max_digits=16)
    deploymentLoss = models.DecimalField(null=False, default=0.0000, decimal_places=4, max_digits=16)
    loadBalancingLoss = models.DecimalField(null=False, default=0.0000, decimal_places=4, max_digits=16)


class Specification(models.Model):
    service = models.ForeignKey(Service, related_name='specification', on_delete=models.CASCADE)
    cause = models.CharField(max_length=200, null=False, blank=False)
    max_initial_loss = models.IntegerField(null=False)
    max_recovery_time = models.IntegerField(null=False)
    max_lor = models.IntegerField(null=False)
