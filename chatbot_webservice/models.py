from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return str(self.name)


class Dependency(models.Model):
    source = models.ForeignKey(Service, related_name='source', on_delete=models.CASCADE)
    target = models.ForeignKey(Service, related_name='target', on_delete=models.CASCADE)

    def __str__(self):
        return self.source.name + " -> " + self.target.name


class ServiceData(models.Model):
    service = models.ForeignKey(Service, related_name='service', on_delete=models.CASCADE)
    time = models.DecimalField(null=False, decimal_places=4, max_digits=10)
    callId = models.IntegerField(null=False)
    successfulTransactions = models.IntegerField(null=False)
    failedTransactions = models.IntegerField(null=False)
    droppedTransactions = models.IntegerField(null=False)
    avgResponseTime = models.DecimalField(null=False, decimal_places=4, max_digits=10)
