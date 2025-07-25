import requests
from django.shortcuts import render
from rest_framework import status
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from .models import MainCategory
from .models import SubCategory, InsuranceStory
from .serializers import ContactMessageSerializer
from .serializers import MainCategorySerializer, SubCategorySerializer
from django.http import JsonResponse
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json, requests
from django.views.generic import ListView, CreateView, DetailView


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


class CategoryDetail(DetailView):
    model = SubCategory
    template_name = "categories/partials/category_detail.html"
    context_object_name = "sub_category"

    def get_object(self):
        self.sub_category = get_object_or_404(SubCategory, slug=self.kwargs['slug'])
        return self.sub_category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_category'], context['main_category'] = self.sub_category, self.sub_category.main_categories.all()
        return context



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


@require_POST
def calculate_insurance(request):
    try:
        coverage = float(request.POST.get('amount', 0))
        age = int(request.POST.get('age', 0))
        type_ = request.POST.get('type')

        # Пример простой формулы
        if type_ == 'life':
            rate = 0.03
        elif type_ == 'auto':
            rate = 0.05
        else:
            rate = 0.02

        if age > 50:
            rate += 0.01

        result = round(coverage * rate, 2)
        return render(request, 'partials/calc_result.html', {'result': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def chat_with_llm(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_prompt = data.get('question', '')
        except Exception as e:
            return JsonResponse({"error": f"Ошибка парсинга JSON: {str(e)}"}, status=400)

        # Формируем системный prompt, добавляя контекст:
        system_prompt = (
            "Ты — страховой консультант, который вежливо и кратко отвечает на вопросы клиентов. "
            "Отвечай по теме страхования в Германии.\n\n"
            "Клиент спрашивает: "
        )
        full_prompt = system_prompt + user_prompt

        payload = {
            "prompt": full_prompt,
            "n_predict": 128,
            "temperature": 0.4,  # можно уменьшить для более точных ответов
            "stop": ["</s>"]
        }

        try:
            url = "http://localhost:8001/completion"
            response = requests.post(url, json=payload, timeout=30)

            try:
                json_data = response.json()
            except Exception as parse_error:
                return JsonResponse({"error": f"LLM не вернул JSON: {parse_error}", "raw": response.text}, status=500)

            return JsonResponse({"answer": json_data.get("content", "Нет ответа")})

        except Exception as e:
            return JsonResponse({"error": f"Ошибка при запросе к LLM: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)
