import django_filters
from django import forms
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Max, Min
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, FormView

from dashboard.utils import CSVParser

from dashboard import models
from rest_framework import permissions, pagination
from rest_framework.fields import SerializerMethodField
from rest_framework.generics import ListAPIView
from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer


# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'


# Create your views here.
class ChartsView(TemplateView):
    template_name = 'charts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_back"] = True
        context["filter"] = EmergencyCallFilter
        return context


class FileImportForm(forms.Form):
    temp_file = forms.FileField(
        label="File to import",
        help_text="Please select or drag-and-drop the file to import.",
        widget=forms.FileInput(attrs={'class': "form-control"})
    )


# Create your views here.
class AdminView(FormView):
    template_name = 'admin.html'
    form_class = FileImportForm
    success_url = reverse_lazy("admin")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_back"] = True
        return context

    def form_valid(self, form):
        temp_file = form.files['temp_file']
        temp_file.seek(0)
        parser = CSVParser(file=temp_file, request=self.request)
        parser.parse()
        # messages.success(self.request, "File successfully uploaded.")
        return super().form_valid(form)


class EmergencyCallMappingSerializer(ModelSerializer):
    class Meta:
        model = models.EmergencyCall
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


class EmergencyCallFilter(django_filters.FilterSet):
    class Meta:
        model = models.EmergencyCall
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

class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class EmergencyCallListAPIView(ListAPIView):
    queryset = models.EmergencyCall.objects.all()
    serializer_class = EmergencyCallMappingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_class = EmergencyCallFilter
    pagination_class = LargeResultsSetPagination

# Create your views here.
class MapView(TemplateView):
    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = models.EmergencyCall.objects.values("datetime").aggregate(max=Max("datetime"), min=Min("datetime"))
        context["datetime_range"] = [qs["min"].strftime("%Y-%m-%d"), qs["max"].strftime("%Y-%m-%d")]
        context["filter"] = EmergencyCallFilter
        context["show_back"] = True
        context["calls"] = [dict(lat=item.latitude, lng=item.longitude) for item in models.EmergencyCall.objects.all()[:1000]]
        return context
