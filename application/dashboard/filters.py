import django_filters

from .models import EmergencyCall


class EmergencyCallFilter(django_filters.FilterSet):
    class Meta:
        model = EmergencyCall
        fields = {
            'category': ['exact'],
            'response_unit': ['exact'],
            'response_unit__response_type': ['exact'],
            "datetime": ["gte", "lte", ],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters["response_unit__response_type"].label = "Response Type"
        self.filters["datetime__gte"].label = "Datetime ≥"
        self.filters["datetime__lte"].label = "Datetime ≤"

        for key in self.form.fields:
            self.form.fields[key].widget.attrs["v-model"] = f"filter.{key}"
            self.form.fields[key].widget.attrs["@change"] = f"updateFilter"

