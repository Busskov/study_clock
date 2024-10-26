import logging
from django.db import IntegrityError
from django.test import TestCase
from .models import User, Activity
from rest_framework.test import APITestCase, APIClient
from .register_serializer import RegisterSerializer
from django.urls import reverse, resolve
from rest_framework import status
from .views import RegisterView, ProtectedView

logger = logging.getLogger(__name__)


class UserManagerTest(TestCase):
    def setUp(self):
        logger.info("Setting up UserManagerTest...")

    def test_create_user(self):
        logger.info("Starting test_create_user")
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            date_of_birth='2000-01-01',
            country='US'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('password123'))
        logger.info("test_create_user passed")

    def test_create_user_missing_fields(self):
        logger.info("Starting test_create_user_missing_fields")
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username='testuser',
                email='',
                password='password123',
                date_of_birth='2000-01-01',
                country='US'
            )
        logger.info("test_create_user_missing_fields passed")

    def test_create_superuser(self):
        logger.info("Starting test_create_superuser")
        admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpass',
            date_of_birth='2000-01-01',
            country='US'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        logger.info("test_create_superuser passed")

    def test_create_superuser_invalid_permissions(self):
        logger.info("Starting test_create_superuser_invalid_permissions")
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username="adminuser",
                email="admin@example.com",
                password="adminpass",
                date_of_birth="2000-01-01",
                country="US",
                is_staff=False
            )
        logger.info("test_create_superuser_invalid_permissions passed")


class UserModelTest(TestCase):
    def setUp(self):
        logger.info("Setting up UserModelTest...")

    def test_user_str(self):
        logger.info("Starting test_user_str")
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            date_of_birth='2000-01-01',
            country='US'
        )
        self.assertEqual(str(user), 'testuser')
        logger.info("test_user_str passed")

    def test_required_fields(self):
        logger.info("Starting test_required_fields")
        with self.assertRaises(ValueError):
            User.objects.create_user(
                username='user',
                email='email@example.com',
                password='pass',
                date_of_birth=None,
                country='US'
            )
        logger.info("test_required_fields passed")

    def test_create_premium_user(self):
        logger.info("Starting test_create_premium_user")
        premium_user = User.objects.create_user(
            username='premiumuser',
            email='premium@example.com',
            password='password123',
            date_of_birth='1990-01-01',
            country='CA',
            is_premium=True
        )
        self.assertTrue(premium_user.is_premium)
        logger.info("test_create_premium_user passed")

    def test_create_user_with_duplicate_email(self):
        logger.info("Starting test_create_user_with_duplicate_email")
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='password123',
            date_of_birth='1995-05-05',
            country='US'
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='user2',
                email='test@example.com',
                password='password456',
                date_of_birth='1995-05-05',
                country='US'
            )
        logger.info("test_create_user_with_duplicate_email passed")


class ActivityModelTest(TestCase):
    def setUp(self):
        logger.info("Setting up ActivityModelTest...")
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            date_of_birth='2000-01-01',
            country='US'
        )
        self.activity = Activity.objects.create(user=self.user, name='Reading')

    def test_activity_str(self):
        logger.info("Starting test_activity_str")
        self.assertEqual(str(self.activity), 'Reading - testuser')
        logger.info("test_activity_str passed")

    def test_add_time(self):
        logger.info("Starting test_add_time")
        self.activity.add_time(30)
        self.assertEqual(self.activity.minutes_spent_today, 30)
        self.assertEqual(self.activity.minutes_spent_this_week, 30)
        self.assertEqual(self.activity.minutes_spent_this_month, 30)
        self.assertEqual(self.activity.minutes_spent_in_total, 30)
        logger.info("test_add_time passed")

    def test_add_multiple_times(self):
        logger.info("Starting test_add_multiple_times")
        self.activity.add_time(30)
        self.activity.add_time(45)
        self.assertEqual(self.activity.minutes_spent_today, 75)
        self.assertEqual(self.activity.minutes_spent_this_week, 75)
        self.assertEqual(self.activity.minutes_spent_this_month, 75)
        self.assertEqual(self.activity.minutes_spent_in_total, 75)
        logger.info("test_add_multiple_times passed")


class RegisterSerializerTest(APITestCase):
    def test_valid_serializer(self):
        logger.info("Starting test_valid_serializer")
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'date_of_birth': '2000-01-01',
            'country': 'US'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        logger.info("test_valid_serializer passed")

    def test_invalid_serializer_missing_fields(self):
        logger.info("Starting test_invalid_serializer_missing_fields")
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'country': 'US'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('date_of_birth', serializer.errors)
        logger.info("test_invalid_serializer_missing_fields passed")

    def test_serializer_with_premium_field(self):
        logger.info("Starting test_serializer_with_premium_field")
        data = {
            'username': 'premiumuser',
            'email': 'premiumuser@example.com',
            'password': 'premium123',
            'date_of_birth': '1995-02-02',
            'country': 'CA',
            'is_premium': True
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertFalse(user.is_premium)
        logger.info("test_serializer_with_premium_field passed")


class RegisterViewTest(APITestCase):
    def setUp(self):
        logger.info("Setting up RegisterViewTest...")
        self.client = APIClient()
        self.url = reverse('register')

    def test_register_user(self):
        logger.info("Starting test_register_user")
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'date_of_birth': '2000-01-01',
            'country': 'US'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'User created successfully')
        self.assertIn('user_id', response.data)
        self.assertTrue(isinstance(response.data['user_id'], int))
        self.assertTrue(User.objects.filter(id=response.data['user_id']).exists())
        logger.info("test_register_user passed")

    def test_register_user_invalid_data(self):
        logger.info("Starting test_register_user_invalid_data")
        data = {'username': 'newuser'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        logger.info("test_register_user_invalid_data passed")


class ProtectedViewTest(APITestCase):
    def setUp(self):
        logger.info("Setting up ProtectedViewTest...")
        self.client = APIClient()
        self.url = reverse('protected_view')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            date_of_birth='2000-01-01',
            country='US'
        )

    def test_access_protected_view_unauthenticated(self):
        logger.info("Starting test_access_protected_view_unauthenticated")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        logger.info("test_access_protected_view_unauthenticated passed")

    def test_access_protected_view_authenticated(self):
        logger.info("Starting test_access_protected_view_authenticated")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'This is a protected view')
        logger.info("test_access_protected_view_authenticated passed")


class URLRoutingTest(TestCase):
    def test_register_url_resolves(self):
        logger.info("Starting test_register_url_resolves")
        url = reverse('register')
        self.assertEqual(resolve(url).func.view_class, RegisterView)
        logger.info("test_register_url_resolves passed")

    def test_protected_view_url_resolves(self):
        logger.info("Starting test_protected_view_url_resolves")
        url = reverse('protected_view')
        self.assertEqual(resolve(url).func.view_class, ProtectedView)
        logger.info("test_protected_view_url_resolves passed")
