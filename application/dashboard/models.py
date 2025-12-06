from django.db import models


class AdministrativeArea(models.Model):
    name = models.CharField(max_length=255)
    zip_code = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('name', 'zip_code')
        ordering = ('zip_code', "name")

class ResponderType(models.Model):
    name = models.CharField(max_length=255)


class ResponseUnit(models.Model):
    responder_type = models.ForeignKey(ResponderType, on_delete=models.CASCADE)
    station_name = models.CharField(max_length=255)


class Category(models.Model):
    name = models.CharField(max_length=255)


class EmergencyCall(models.Model):
    datetime = models.DateTimeField()
    response_unit = models.ForeignKey(ResponseUnit, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
