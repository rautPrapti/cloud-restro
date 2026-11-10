from django.test import TestCase
from django.urls import reverse
# Create your tests here.

class ResturantTests(TestCase):
    def test_homepage_status_code(self):
        response=self.client.get(reverse('home'))

        self.assertEqual(response.status_code,200)

    def test_menu_page_status_code(self):
        response = self.client.get(reverse('menu'))

        self.assertEqual(response.status_code, 200)

    def test_food_api_status_code(self):
        response = self.client.get(reverse('food_api'))

        self.assertEqual(response.status_code, 200)

    def test_food_api_returns_list(self):
        response = self.client.get(reverse('food_api'))

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_my_orders_requires_login(self):
        response = self.client.get(reverse('my_orders'))

        self.assertEqual(response.status_code, 302)