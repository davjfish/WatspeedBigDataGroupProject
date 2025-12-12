from django.db.models import Max, Min, Count
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from .filters import EmergencyCallFilter
from .forms import FileImportForm
from .paginators import LargeResultsSetPagination
from .parsers import PA911CSVParser
from .serializers import EmergencyCallMappingSerializer
from . import models


# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'


# Create your views here.
class ChartsView(TemplateView):
    template_name = 'charts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_back"] = True
        qs = models.EmergencyCall.objects.values("datetime").aggregate(max=Max("datetime"), min=Min("datetime"))
        context["datetime_range"] = [qs["min"].strftime("%Y-%m-%d"), qs["max"].strftime("%Y-%m-%d")]
        context["filter"] = EmergencyCallFilter
        return context


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
        file_format = form.cleaned_data['file_format']
        temp_file.seek(0)
        if format == format:
            parser = PA911CSVParser(file=temp_file, request=self.request)
            parser.parse()
        # messages.success(self.request, "File successfully uploaded.")
        return super().form_valid(form)


class EmergencyCallListAPIView(ListAPIView):
    queryset = models.EmergencyCall.objects.all()
    serializer_class = EmergencyCallMappingSerializer
    filterset_class = EmergencyCallFilter
    pagination_class = LargeResultsSetPagination

    def list(self, request, *args, **kwargs):
        qp = request.query_params
        if qp.get("chart1"):
            queryset = self.filter_queryset(self.get_queryset())
            queryset = list(queryset.order_by("category").values("category").distinct().annotate(count=Count("id")))
            queryset.sort(key=lambda x: x["count"], reverse=True)
            category_lookup = {item.id: str(item) for item in models.Category.objects.all()}
            categories = [category_lookup[item["category"]] for item in queryset]
            counts = [item["count"] for item in queryset]
            return Response(dict(labels=categories, counts=counts), status=HTTP_200_OK)
        return super().list(request, *args, **kwargs)


# Create your views here.
class MapView(TemplateView):
    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = models.EmergencyCall.objects.values("datetime").aggregate(max=Max("datetime"), min=Min("datetime"))
        context["datetime_range"] = [qs["min"].strftime("%Y-%m-%d"), qs["max"].strftime("%Y-%m-%d")]
        context["filter"] = EmergencyCallFilter
        context["show_back"] = True
        return context
