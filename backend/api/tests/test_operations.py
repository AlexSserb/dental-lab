from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import Group
from django.core.serializers import serialize
from datetime import datetime
from uuid import uuid4

from accounts.models import User
from api.models import *


class OperationsTest(TestCase):
    """
        Integration tests for operations and dental technicians
    """
    fixtures: list[str] = [
        './api/fixtures/groups_data.json', 
        './api/fixtures/test_data_statuses.json',
        './api/fixtures/operation_and_product_types.json'
    ]

    email: str = 'alex@mail.com'
    password: str = '12345678sa'
    first_name: str = 'Alex'
    last_name: str = 'Serb'
    URL: str = '/api'

    @classmethod
    def setUpTestData(cls):
        cls.user = User(id=1, email=cls.email, first_name=cls.first_name, last_name=cls.last_name)
        cls.user.set_password(cls.password)
        cls.user.save()
        cls.user.groups.add(3)

    def setUp(self):
        response = self.client.post('/accounts/token/', data={'email': self.email, 'password': self.password})
        self.token = response.data['access']
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_get_operations_for_tech_correct(self):
        # region set test data
        order = Order.objects.create(user=self.user, discount=0.05, status=OrderStatus.objects.get(number=3))
        product = Product.objects.create(product_status=ProductStatus.objects.get(number=3),
            product_type=ProductType.objects.get(name='Product type 2'), order=order, amount=2)

        operation_status = OperationStatus.objects.get(number=2)
        operation1 = Operation.objects.create(product=product, tech=self.user, operation_status=operation_status,
            operation_type=OperationType.objects.get(name='Operation type 3'))
        operation2 = Operation.objects.create(product=product, tech=self.user, operation_status=operation_status,
            operation_type=OperationType.objects.get(name='Operation type 2'))
        # endregion 
        
        response = self.client.get(self.URL + '/operations_for_tech/')
        resp: list = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(resp), 2)
        if resp[0]['operation_type']['name'] != 'Operation type 3':
            resp[0], resp[1] = resp[1], resp[0]
        self.assertTrue(resp[0]['operation_status']['name'] == resp[1]['operation_status']['name'] == 'At work')
        self.assertEqual(resp[0]['operation_type']['name'], 'Operation type 3')
        self.assertEqual(resp[1]['operation_type']['name'], 'Operation type 2')
        self.assertTrue(resp[0]['product']['product_type']['name'] == \
            resp[1]['product']['product_type']['name'] == 'Product type 2')
        
    def test_get_operations_for_tech_incorrect_token(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token + '1')
        response = client.get(self.URL + '/operations_for_tech/')

        self.assertEqual(response.status_code, 401)

    def test_set_operation_status_correct(self):
        # region set test data
        order = Order.objects.create(user=self.user, discount=0, status=OrderStatus.objects.get(number=3))
        product = Product.objects.create(product_status=ProductStatus.objects.get(number=3),
            product_type=ProductType.objects.get(name='Product type 2'), order=order, amount=1)

        operation = Operation.objects.create(product=product, tech=self.user, 
            operation_status=OperationStatus.objects.get(number=2),
            operation_type=OperationType.objects.get(name='Operation type 3'))
        # endregion
        
        response = self.client.patch(self.URL + f'/operation/{operation.id}/', 
            data={'status_id': 'efee01cc-e81b-4936-8580-33e778ae0f67'}, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['operation_type']['name'], 'Operation type 3')
        self.assertEqual(response.data['operation_status']['name'], 'Ready')
        
    def test_set_operation_status_incorrect_token(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token + '1')
        response = client.patch(self.URL + f'/operation/1/', data={"status_id": 123}, follow=True)

        self.assertEqual(response.status_code, 401)

    def test_set_operation_status_incorrect_operation_id(self):
        incorrect_id = 'efee01cc-e81b-4936-8580-33e778ae0f67'

        response = self.client.patch(self.URL + f'/operation/{incorrect_id}/', 
            data={'status_id': 'efee01cc-e81b-4936-8580-33e778ae0f67'}, follow=True)
        
        self.assertEqual(response.status_code, 404)

    def test_get_all_operation_statuses_correct(self):
        response = self.client.get(self.URL + '/operation_statuses/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(set(st['name'] for st in response.data), set((
            'The work has not started', 'At work', 'Ready'
        )))
        
    def test_get_all_operation_statuses_incorrect_token(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token + '1')
        response = client.get(self.URL + '/operation_statuses/')

        self.assertEqual(response.status_code, 401)
        