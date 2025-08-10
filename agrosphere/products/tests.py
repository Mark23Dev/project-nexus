from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Product, Category

User = get_user_model()

class ProductAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="vendor@example.com", password="pass1234")
        self.category = Category.objects.create(name="Electronics")
        self.client.force_authenticate(user=self.user)

        self.product = Product.objects.create(
            vendor=self.user,
            category=self.category,
            title="Test Product",
            price=100,
            available=True,
        )

    def test_list_products(self):
        url = reverse("products:products-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_create_product(self):
        url = reverse("products:products-list")
        data = {
            "title": "New Product",
            "category_id": self.category.id,
            "price": 50,
            "available": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "New Product")

    def test_filter_products_by_category(self):
        url = reverse("products:products-list") + "?category=electronics"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(p["category"]["slug"] == "electronics" for p in response.data))

    def test_update_product(self):
        url = reverse("products:products-detail", args=[self.product.id])
        data = {
            "title": "Updated Product",
            "price": 150,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.title, "Updated Product")
        self.assertEqual(float(self.product.price), 150)

    def test_delete_product(self):
        url = reverse("products:products-detail", args=[self.product.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())
