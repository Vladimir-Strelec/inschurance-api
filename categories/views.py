from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ContactMessageSerializer
from .models import MainCategory, SubCategory, InsuranceStory
from .serializers import MainCategorySerializer, SubCategorySerializer

from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from .models import MainCategory


class MainCategoryViewSet(viewsets.ModelViewSet):
    queryset = MainCategory.objects.all()
    serializer_class = MainCategorySerializer


class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


def category_ui(request):
    stories = InsuranceStory.objects.order_by('-created_at')[:10]
    return render(request, 'main.html', {
        'categories': MainCategory.objects.prefetch_related('subcategories'),
        'stories': stories
    })


@require_POST
def create_main_category(request):
    name = request.POST.get("name")
    if name:
        MainCategory.objects.create(name=name)
    categories = MainCategory.objects.prefetch_related('subcategories')
    return render(request, 'categories/partials/list.html', {'categories': categories})


class ContactMessageView(APIView):
    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if request.headers.get("Hx-Request"):
                return render(request, "categories/contact_success.html")
            return Response(serializer.data)
        if request.headers.get("Hx-Request"):
            return render(request, "categories/contact_form.html", {"errors": serializer.errors})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)