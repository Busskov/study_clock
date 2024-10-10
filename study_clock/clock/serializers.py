from rest_framework import serializers
from .models import User
class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "login", "password_hash", "date_of_birth",
                  "email", "country", "is_premium"]