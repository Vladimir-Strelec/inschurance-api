from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MainCategoryViewSet, SubCategoryViewSet, category_ui, create_main_category, ContactMessageView

router = DefaultRouter()
router.register(r'main-categories', MainCategoryViewSet)
router.register(r'sub-categories', SubCategoryViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('categories-ui/', category_ui, name='category_ui'),
    path('categories-ui/create/', create_main_category, name='create_main_category'),
    path('api/contact/', ContactMessageView.as_view(), name='contact_api'),

]
