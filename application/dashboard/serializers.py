from django.contrib.humanize.templatetags.humanize import naturaltime
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer

from .models import EmergencyCall


class EmergencyCallMappingSerializer(ModelSerializer):
    class Meta:
        model = EmergencyCall
        fields = [
            "latitude",
            "longitude",
            "category",
            "response_unit",
            "response_type",
            "dt_display",
        ]

    category = StringRelatedField()
    response_unit = StringRelatedField()
    dt_display = SerializerMethodField()
    response_type = SerializerMethodField()

    def get_dt_display(self, instance):
        return naturaltime(instance.datetime)

    def get_response_type(self, instance):
        return instance.response_unit.response_type.name

