from rest_framework import serializers

from clock.models import User


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'date_of_birth', 'country')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            date_of_birth=validated_data['date_of_birth'],
            country=validated_data['country']
        )
        return user