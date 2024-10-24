from django.test import TestCase
from .models import User, Activity


class UserTest(TestCase):
    def test_create_user(self):
        user = User.objects.create(
            login='testuser',
            password_hash='hashed_password',
            email='testuser@example.com',
            date_of_birth='2000-01-01',
            country='US',
            is_premium=False
        )
        self.assertEqual(user.login, 'testuser')
