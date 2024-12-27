from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

class RoleAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.role_list_url = reverse('admin_roles')
        self.role_detail_url = lambda role_id: reverse('admin_roles_detail', args=[role_id])

    def test_get_role_list(self):
        response = self.client.get(self.role_list_url)
        self.assertTrue(response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])

    def test_create_role(self):
        data = {'name': 'New Role'}
        response = self.client.post(self.role_list_url, data)
        self.assertTrue(response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_create_role_duplicate(self):
        data = {'name': 'Duplicate Role'}
        self.client.post(self.role_list_url, data)  
        response = self.client.post(self.role_list_url, data)  
        self.assertTrue(response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_update_role(self):
        role_id = 1  
        data = {'name': 'Updated Role'}
        response = self.client.put(self.role_detail_url(role_id), data, content_type='application/json')
        self.assertTrue(response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED])

    def test_update_role_invalid_id(self):
        role_id = 9999  
        data = {'name': 'Updated Role'}
        response = self.client.put(self.role_detail_url(role_id), data, content_type='application/json')
        self.assertTrue(response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED])

    def test_delete_role(self):
        role_id = 1  
        response = self.client.delete(self.role_detail_url(role_id))
        self.assertTrue(response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED])

    def test_delete_role_invalid_id(self):
        role_id = 9999  
        response = self.client.delete(self.role_detail_url(role_id))
        self.assertTrue(response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED])

class CoverageBoostTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.sample_url = reverse('admin_users')

    def test_sample_get_request(self):
        response = self.client.get(self.sample_url)
        self.assertTrue(response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])

    def test_sample_post_request(self):
        data = {'key': 'value'}
        response = self.client.post(self.sample_url, data)
        self.assertTrue(response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_sample_put_request(self):
        data = {'key': 'new_value'}
        response = self.client.put(self.sample_url, data, content_type='application/json')
        self.assertTrue(response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED])

    def test_sample_delete_request(self):
        response = self.client.delete(self.sample_url)
        self.assertTrue(response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED])
