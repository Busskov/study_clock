from django.contrib.auth.models import AbstractUser
from django.db import models
from django_countries.fields import CountryField
from clock.managers import UserManager
import logging

logger = logging.getLogger(__name__)


class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, verbose_name='Username')
    date_of_birth = models.DateField(verbose_name='Date of Birth')
    email = models.EmailField(unique=True, verbose_name='Email Address')
    country = CountryField(verbose_name='Country')
    is_premium = models.BooleanField(default=False, verbose_name='Premium User')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Avatar')

    objects = UserManager()
    REQUIRED_FIELDS = ['email', 'date_of_birth', 'country']

    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=50, verbose_name='Activity Name')
    minutes_spent_today = models.PositiveIntegerField(default=0, verbose_name='Minutes Spent Today')
    minutes_spent_this_week = models.PositiveIntegerField(default=0, verbose_name='Minutes Spent This Week')
    minutes_spent_this_month = models.PositiveIntegerField(default=0, verbose_name='Minutes Spent This Month')
    minutes_spent_in_total = models.PositiveIntegerField(default=0, verbose_name='Minutes Spent in Total')

    class Meta:
        db_table = 'activity'
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f'{self.name} - {self.user.username}'

    def add_time(self, minutes):
        logger.debug('Adding time for activity %s: %d minutes', self.name, minutes)
        self.minutes_spent_today += minutes
        self.minutes_spent_this_week += minutes
        self.minutes_spent_this_month += minutes
        self.minutes_spent_in_total += minutes
        self.save()
        logger.info('Time added for activity %s. Today is time: %d minutes', self.name, self.minutes_spent_today)
