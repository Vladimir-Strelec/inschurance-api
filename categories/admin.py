from django.contrib import admin

from categories.models import MainCategory, SubCategory

admin.site.register(MainCategory)
admin.site.register(SubCategory)
