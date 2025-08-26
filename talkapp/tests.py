from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse


class CustomUserCreateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_creation(self):
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'password': 'securepassword123',
            'firstname': 'John',
            'lastname': 'Doe',
            'university': 'Sample University',
            'user_role': 'student',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['email'], 'test@example.com')
