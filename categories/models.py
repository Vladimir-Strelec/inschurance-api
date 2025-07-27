from django.db import models
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.reverse import reverse


class MainCategory(models.Model):
    name = models.CharField(max_length=100)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('main_category_list', args=[self.slug])

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    private = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True)
    main_categories = models.ManyToManyField(MainCategory, related_name="subcategories")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('sub_category_list', args=[self.slug])

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    email = models.EmailField()
    phone = PhoneNumberField(region='DE')
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


class InsuranceStory(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    url = models.URLField(blank=True, help_text="Ссылка на полную историю (опционально)")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
