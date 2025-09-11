from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.sitemaps.views import sitemap
from .views import MainCategoryViewSet, SubCategoryViewSet, category_ui, create_main_category, ContactMessageView, \
    calculate_insurance, chat_with_llm, CategoryDetail, robots_txt
from .sitemaps import StorySitemap, SubCategorySitemap, MainCategorySitemap
from .views import gsc_verification

router = DefaultRouter()
router.register(r'main-categories', MainCategoryViewSet)
router.register(r'sub-categories', SubCategoryViewSet)

# добавлено: словарь карт сайта
sitemaps = {
    'stories': StorySitemap,
    'subcategories': SubCategorySitemap,
    'maincategories': MainCategorySitemap,
}

urlpatterns = [
    path('api/', include(router.urls)),
    path('', category_ui, name='category_ui'),
    path('categories/category_detail/<slug:slug>', CategoryDetail.as_view(), name='category_detail'),
    path('categories-ui/create/', create_main_category, name='create_main_category'),


    path('api/contact/', ContactMessageView.as_view(), name='contact_form_partial'),
    path('calculate/', calculate_insurance, name='calculate_insurance'),
    path('api/chat/', chat_with_llm, name='chat_with_llm'),
    path('api/contact/', ContactMessageView.as_view(), name='contact_api'),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("googlebe58e3a7529dfcf2.html", gsc_verification, name="gsc_verification"),
]
