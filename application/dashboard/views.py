import django_filters
from django import forms
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime
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
class MapView(TemplateView):
    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_back"] = True
        context["calls"] = [dict(lat=item.latitude, lng=item.longitude) for item in models.EmergencyCall.objects.all()[:1000]]
        return context


# Create your views here.
class ChartsView(TemplateView):
    template_name = 'charts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_back"] = True
        context["areas"] = models.Township.objects.all()
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
            "dt_display",
        ]

    category = StringRelatedField()
    response_unit = StringRelatedField()
    dt_display = SerializerMethodField()

    def get_dt_display(self, instance):
        return naturaltime(instance.datetime)


class EmergencyCallFilter(django_filters.FilterSet):
    # date_range = django_filters.DateRangeFilter(field_name="datetime", lookup_expr="range")
    date_range = django_filters.DateFromToRangeFilter(field_name="datetime", lookup_expr="range")

    class Meta:
        model = models.EmergencyCall
        fields = {
            'category': ['exact'],
            'response_unit__response_type': ['exact'],
        }


class EmergencyCallListAPIView(ListAPIView):
    queryset = models.EmergencyCall.objects.all()
    serializer_class = EmergencyCallMappingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    page_size_query_param = "page_size"
    filterset_class = EmergencyCallFilter
