from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register-list")  # router name used earlier
        self.token_url = reverse("token_obtain_pair")

    def test_register_user(self):
        data = {
            "email": "alice@example.com",
            "password": "StrongPassword!1",
            "password2": "StrongPassword!1",
            "first_name": "Alice"
        }
        resp = self.client.post(self.register_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="alice@example.com").exists())

    def test_login_after_register(self):
        reg_data = {
            "email": "bob@example.com",
            "password": "StrongPassword!1",
            "password2": "StrongPassword!1",
            "first_name": "Bob"
        }
        self.client.post(self.register_url, reg_data, format="json")
        login_resp = self.client.post(self.token_url, {"email": "bob@example.com", "password": "StrongPassword!1"}, format="json")
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_resp.data)


class UserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="carol@example.com", password="pass12345")
        self.me_url = reverse("users-me")  # action 'me' defined in viewset

    def test_get_my_profile_requires_auth(self):
        resp = self.client.get(self.me_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_my_profile(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.me_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["email"], "carol@example.com")
