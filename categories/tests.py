from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import requests
from categories.models import MainCategory


class MainCategoryViewSetTest(APITestCase):
    def setUp(self):
        self.category = MainCategory.objects.create(name='Test category', image_url='https://img.freepik.com/free-photo/beautiful-view-sunset-sea_23-2148019892.jpg?size=626&ext=jpg',
                                                    slug='slug-test')

        self.list_url = reverse('category_ui')
        self.detail_url = reverse('category_detail', args=[self.category.slug])

    def test_get_category_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_name_created(self):
        self.assertEqual(self.category.name, 'Test category')

    def test_image_url_accessible(self):
        url = self.category.image_url
        try:
            r = requests.get(url, timeout=5)
            self.assertEqual(r.status_code, 200)
            self.assertIn(r.headers['Content-Type'], ['image/jpeg', 'image/png', 'image/gif', 'image/webp'])
        except requests.RequestException:
            self.fail(f"URL {url} не доступен")

    def test_create_slug(self):
        self.assertEqual(self.category.slug, 'slug-test')
