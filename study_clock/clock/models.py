from django.db import models

class User(models.Model):
    login = models.CharField(max_length= 50, unique=True)
    password_hash = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)
    country = models.CharField(max_length = 30)
    is_premium = models.BooleanField()

    class Meta:
        db_table = 'user'



class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    minutes_spent_today = models.IntegerField()
    minutes_spent_this_week = models.IntegerField()
    minutes_spent_this_month = models.IntegerField()
    minutes_spent_in_total = models.IntegerField()

    class Meta:
        db_table = 'activity'
