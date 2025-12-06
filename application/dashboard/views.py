from django import forms
from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, FormView

from dashboard.utils import CSVParser

from dashboard import models


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
