

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from rest_framework.test import force_authenticate
from users.models import User,OTP

class TestPost(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(email='testverified@gmail.com',verified=True)
        

        self.client2 = APIClient()
        self.user2 = User.objects.create(phone='+8801716247545')
        self.client2.force_authenticate(user=self.user2)

    
    def test_user_can_register_with_email(self):

        url = '/auth/register/'

        data = {
           'input': 'test1@gmail.com',
           'password': '123456'
        }

        response = self.client.post(url,data,format='multipart')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'],'Email send to test1@gmail.com')

    def test_user_can_register_with_phone(self):

        url = '/auth/register/'

        data = {
           'input': '+880171123133',
           'password': '123456'
        }

        response = self.client.post(url,data,format='multipart')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'],'Sms send to +880171123133')

   