from django.contrib import admin

from categories.models import MainCategory, SubCategory, ContactMessage, InsuranceStory

admin.site.register(MainCategory)
admin.site.register(SubCategory)
admin.site.register(ContactMessage)
admin.site.register(InsuranceStory)
