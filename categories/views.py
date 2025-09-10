import requests
from django.shortcuts import render
from rest_framework import status
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest, HttpResponse
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
from django.core.cache import cache
import uuid, hashlib

from .utils import get_or_create_lead_key


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
    def get(self, request):
        # Рендер большой формы с тем же самым сессионным ключом
        key = get_or_create_lead_key(request)
        is_mini = request.GET.get("mini") == "1"
        return render(request, "categories/contact_form.html", {"is_mini": is_mini, "uuid": key})

    def post(self, request):
        # Берем ключ из заголовка или поля. Если нет — подставим из сессии, чтобы не падать.
        key = (
            request.headers.get("Idempotency-Key")
            or request.data.get("idempotency_key")
            or request.session.get("lead_idemp")
        )
        if not key:
            return Response({"detail": "Missing idempotency key"}, status=400)

        # Блокируем дубли по ключу
        if cache.get(f"idemp:{key}"):
            # Для HTMX вернём тот же самый success, чтобы UI не мигал ошибками
            is_htmx = request.headers.get("HX-Request") == "true" or request.headers.get("Hx-Request") == "true"
            if is_htmx:
                is_mini = (request.data.get("mini") == "1") or (request.POST.get("mini") == "1")
                return render(request, "categories/contact_success.html", {"is_mini": is_mini}, status=200)
            return Response({"detail": "Duplicate"}, status=409)

        serializer = ContactMessageSerializer(data=request.data)
        if not serializer.is_valid():
            # Для HTMX возвращаем ту же частичку формы с ошибками
            is_htmx = request.headers.get("HX-Request") == "true" or request.headers.get("Hx-Request") == "true"
            is_mini = (request.data.get("mini") == "1") or (request.POST.get("mini") == "1")
            if is_htmx:
                return render(request, "categories/contact_form.html", {"errors": serializer.errors, "is_mini": is_mini, "uuid": key}, status=400)
            return Response(serializer.errors, status=400)

        obj = serializer.save()

        # Фиксируем ключ на 5 минут
        cache.set(f"idemp:{key}", True, timeout=300)

        is_htmx = request.headers.get("HX-Request") == "true" or request.headers.get("Hx-Request") == "true"
        is_mini = (request.data.get("mini") == "1") or (request.POST.get("mini") == "1")

        if is_htmx:
            # Мини и большая HTMX‑форма получат локальный success
            return render(request, "categories/contact_success.html", {"is_mini": is_mini}, status=201)

        # НЕ-HTMX большая форма: рендерим полноценную страницу успеха
        return render(request, "categories/contact_success_page.html", {"id": obj.id}, status=201)

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


def contact_form_partial(request):
    # ВСЕГДА один и тот же ключ из сессии
    key = get_or_create_lead_key(request)
    return render(
        request,
        "categories/contact_form.html",   # та же частичка формы
        {"is_mini": True, "uuid": key}
    )


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /",
        "Sitemap: https://inschurance.online/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")