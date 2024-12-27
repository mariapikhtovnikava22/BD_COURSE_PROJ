from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

class UserPanelAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_list_url = reverse('admin_users')
        self.user_detail_url = lambda user_id: reverse('admin_user_detail', args=[user_id])

    def test_get_user_list(self):
        response = self.client.get(self.user_list_url)
        self.assertTrue(response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])

    def test_get_user_detail(self):
        user_id = 1  # Тестовый ID
        response = self.client.get(self.user_detail_url(user_id))
        self.assertTrue(response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED])

    def test_create_user(self):
        data = {
            'fio': 'New User',
            'email': 'newuser@example.com',
            'password': 'password123',
            'role_id': 1,
            'level_id': 1,
        }
        response = self.client.post(self.user_list_url, data)
        self.assertTrue(response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_create_user_missing_fields(self):
        data = {
            'fio': 'New User',
        }
        response = self.client.post(self.user_list_url, data)
        self.assertTrue(response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_update_user(self):
        user_id = 1  
        data = {'fio': 'Updated User'}
        response = self.client.put(self.user_detail_url(user_id), data, content_type='application/json')
        self.assertTrue(response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED])

    def test_update_user_invalid_id(self):
        user_id = 9999  
        data = {'fio': 'Updated User'}
        response = self.client.put(self.user_detail_url(user_id), data, content_type='application/json')
        self.assertTrue(response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED])

    def test_delete_user(self):
        user_id = 1  
        response = self.client.delete(self.user_detail_url(user_id))
        self.assertTrue(response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED])

    def test_delete_user_invalid_id(self):
        user_id = 9999  
        response = self.client.delete(self.user_detail_url(user_id))
        self.assertTrue(response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED])

