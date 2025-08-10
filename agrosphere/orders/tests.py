from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product, Category
from .models import Order

User = get_user_model()

class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='buyer@example.com', password='pass1234')
        self.client.force_authenticate(user=self.user)

        category = Category.objects.create(name="Books")
        self.product = Product.objects.create(
            title="Test Book",
            price=20,
            available=True,
            category=category,
            vendor=self.user
        )

    def test_create_order(self):
        url = reverse('orders-list')
        data = {
            "shipping_address": "123 Street",
            "billing_address": "123 Street",
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 2
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['total_price'], '40.00')

    def test_user_cannot_modify_others_order(self):
        # Create an order for another user
        other_user = User.objects.create_user(email='other@example.com', password='pass1234')
        order = Order.objects.create(user=other_user, shipping_address="Addr")
        url = reverse('orders-detail', args=[order.id])
        data = {"shipping_address": "Changed Address"}

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
