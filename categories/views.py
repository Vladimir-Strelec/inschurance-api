import requests
from django.shortcuts import render
from rest_framework import status
from rest_framework import viewsets
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


from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # просто пропускаем проверку


class ChatBotView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    def post(self, request):
        question = request.data.get("question")

        if not question:
            return Response({"error": "Вопрос не передан."}, status=status.HTTP_400_BAD_REQUEST)

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

        try:
            completion = client.chat.completions.create(
                model="openai/gpt-4.1",
                messages=[{
                    "role": "user",
                    "content": [{"type": "text", "text": question}]
                }],
                max_tokens = 1000
            )

            reply = completion.choices[0].message.content
            return Response({"answer": reply})

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)