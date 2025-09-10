# sitemaps.py
from django.contrib.sitemaps import Sitemap
from .models import InsuranceStory, MainCategory, SubCategory


class StorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        # Если есть статус публикации — фильтруй тут. Иначе оставь .all()
        return InsuranceStory.objects.all()

    def location(self, obj):
        # Если у модели реализован get_absolute_url, можешь удалить этот метод.
        return f"/story/{obj.slug}/"

    def lastmod(self, obj):
        # Вернёт дату, если есть updated_at или created_at; иначе None.
        return getattr(obj, "updated_at", getattr(obj, "created_at", None))


class MainCategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return MainCategory.objects.all()

    def location(self, obj):
        return f"/{obj.slug}/"

    def lastmod(self, obj):
        return getattr(obj, "updated_at", getattr(obj, "created_at", None))


class SubCategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return SubCategory.objects.all()

    def location(self, obj):
        """
        Если связь с главной категорией M2M (obj.main_category.first()),
        соберём URL как /<main>/<sub>/. Если FK — возьмём напрямую.
        Если главной категории нет — вернём /<sub>/.
        """
        main_cat = None
        # Попробуем как M2M (например, ManyToManyField)
        if hasattr(obj, "main_category") and hasattr(obj.main_category, "all"):
            main_cat = obj.main_category.first()
        # Или как FK (ForeignKey)
        elif hasattr(obj, "main_category"):
            main_cat = getattr(obj, "main_category", None)

        if main_cat:
            return f"/{main_cat.slug}/{obj.slug}/"
        return f"/{obj.slug}/"

    def lastmod(self, obj):
        return getattr(obj, "updated_at", getattr(obj, "created_at", None))
