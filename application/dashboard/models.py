from django.db import models


class Township(models.Model):
    state = models.CharField(max_length=10, verbose_name="State abbreviation", default="PA")
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ("state", "name")
        unique_together = [("state", "name"), ]

    def __str__(self):
        return f"{self.name}, {self.state} "


class ResponderType(models.Model):
    name = models.CharField(max_length=255)


class Category(models.Model):
    name = models.CharField(max_length=255)


class ResponseUnit(models.Model):
    responder_type = models.ForeignKey(ResponderType, on_delete=models.CASCADE)
    station_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('responder_type', 'station_name')
        ordering = ('responder_type', "station_name")


class EmergencyCall(models.Model):
    datetime = models.DateTimeField()
    response_unit = models.ForeignKey(ResponseUnit, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    township = models.ForeignKey(Township, on_delete=models.CASCADE, blank=True, null=True)
    zip_code = models.SmallIntegerField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
