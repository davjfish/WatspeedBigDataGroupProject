from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'


# Create your views here.
class DashboardView(TemplateView):
    template_name = 'dashboard.html'


# Create your views here.
class AdminView(TemplateView):
    template_name = 'admin.html'
