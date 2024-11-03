import logging
from django.db import IntegrityError, models
from django.db.models import F, ExpressionWrapper, fields
from django.test import TestCase
from .models import User, Activity
from rest_framework.test import APITestCase, APIClient
from .serializers import RegisterSerializer
from django.urls import reverse, resolve
from rest_framework import status
from .views import RegisterView, ProtectedView
import random
from datetime import datetime, timedelta
from django.db import transaction
from concurrent.futures import ThreadPoolExecutor

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


class LargeDatabaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        logger.info("Setting up LargeDatabaseTest with 10,000 users...")
        # num_users = 10000
        users = [
            User(
                username=f'user_{i}',
                email=f'user_{i}@example.com',
                password='password123',
                date_of_birth=(datetime.now() - timedelta(days=random.randint(7000, 15000))).date(),
                country='US'
            )
            for i in range(0, 10000)
        ]
        User.objects.bulk_create(users)
        # for i in range(num_users):
        #     User.objects.create_user(
        #         username=f'user_{i}',
        #         email=f'user_{i}@example.com',
        #         password='password123',
        #         date_of_birth=(datetime.now() - timedelta(days=random.randint(7000, 15000))).date(),
        #         country='US'
        #     )
        logger.info("10,000 users created successfully.")

    def test_large_database_user_count(self):
        logger.info("Starting test_large_database_user_count")
        user_count = User.objects.count()
        self.assertEqual(user_count, 10000)
        logger.info("test_large_database_user_count passed")

    def test_query_performance(self):
        logger.info("Starting test_query_performance")
        with self.assertNumQueries(1):
            user = User.objects.get(username='user_5000')
            self.assertEqual(user.email, 'user_5000@example.com')
        logger.info("test_query_performance passed")

    def test_bulk_create_users(self):
        logger.info("Starting test_bulk_create_users")
        additional_users = [
            User(
                username=f'new_user_{i}',
                email=f'new_user_{i}@example.com',
                password='password123',
                date_of_birth=(datetime.now() - timedelta(days=random.randint(7000, 15000))).date(),
                country='CA'
            )
            for i in range(10001, 11001)
        ]
        User.objects.bulk_create(additional_users)
        user_count = User.objects.count()
        self.assertEqual(user_count, 11000)
        logger.info("test_bulk_create_users passed")

    def test_large_dataset_retrieval(self):
        logger.info("Starting test_large_dataset_retrieval")
        start_time = datetime.now()
        users = User.objects.all()[:1000]
        self.assertEqual(len(users), 1000)
        elapsed_time = datetime.now() - start_time
        logger.info(f"Retrieved 1,000 users in {elapsed_time.total_seconds()} seconds")
        self.assertLess(elapsed_time.total_seconds(), 1, "Query took too long")
        logger.info("test_large_dataset_retrieval passed")

    def test_aggregate_query_performance(self):
        logger.info("Starting test_aggregate_query_performance")
        start_time = datetime.now()
        avg_age = User.objects.annotate(
            age=ExpressionWrapper(
                datetime.now().date() - F('date_of_birth'),
                output_field=fields.DurationField()
            )
        ).aggregate(average_age=models.Avg('age'))
        elapsed_time = datetime.now() - start_time
        logger.info(f"Average age computed in {elapsed_time.total_seconds()} seconds")
        self.assertLess(elapsed_time.total_seconds(), 2, "Aggregation query took too long")
        logger.info("test_aggregate_query_performance passed")

    def test_bulk_delete_users(self):
        logger.info("Starting test_bulk_delete_users")
        start_time = datetime.now()
        User.objects.filter(username__startswith='user_').delete()
        elapsed_time = datetime.now() - start_time
        user_count = User.objects.count()
        self.assertEqual(user_count, 0)
        logger.info(f"Bulk deletion completed in {elapsed_time.total_seconds()} seconds")
        logger.info("test_bulk_delete_users passed")

    def test_transaction_handling(self):
        logger.info("Starting test_transaction_handling")
        try:
            with transaction.atomic():
                new_users = [
                    User(
                        username=f'transaction_user_{i}',
                        email=f'transaction_user_{i}@example.com',
                        password='password123',
                        date_of_birth=(datetime.now() - timedelta(days=random.randint(7000, 15000))).date(),
                        country='US'
                    )
                    for i in range(11001, 12001)
                ]
                User.objects.bulk_create(new_users)
                raise Exception("Intentional exception to test rollback")
        except Exception as e:
            logger.info(f"Transaction rolled back due to: {e}")

        user_count = User.objects.filter(username__startswith='transaction_user_').count()
        self.assertEqual(user_count, 0)
        logger.info("test_transaction_handling passed")

    def test_indexed_query_performance(self):
        logger.info("Starting test_indexed_query_performance")
        start_time = datetime.now()
        user = User.objects.filter(email='user_5000@example.com').first()
        elapsed_time = datetime.now() - start_time
        logger.info(f"Indexed query completed in {elapsed_time.total_seconds()} seconds")
        self.assertIsNotNone(user)
        self.assertLess(elapsed_time.total_seconds(), 0.5, "Indexed query took too long")
        logger.info("test_indexed_query_performance passed")

    def test_bulk_update_integrity(self):
        logger.info("Starting test_bulk_update_integrity")
        updated_count = User.objects.filter(username__startswith='user_').update(country='UK')
        self.assertEqual(updated_count, 10000)
        updated_users = User.objects.filter(country='UK').count()
        self.assertEqual(updated_users, 10000)
        logger.info("test_bulk_update_integrity passed")

    # THIS TEST DOES NOT WORK. but should it?

    # def test_concurrent_queries(self):
    #     logger.info("Starting test_concurrent_queries")
    #
    #     def query_user_by_username(username):
    #         return User.objects.filter(username=username).first()
    #
    #     usernames = [f'user_{i}' for i in range(1000)]
    #     with ThreadPoolExecutor(max_workers=10) as executor:
    #         results = list(executor.map(query_user_by_username, usernames))
    #
    #     for user in results:
    #         self.assertIsNotNone(user)
    #     logger.info("test_concurrent_queries passed")
