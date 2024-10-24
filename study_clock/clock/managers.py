from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, username, email, date_of_birth, country, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not date_of_birth:
            raise ValueError('The Date of Birth field must be set')
        if not country:
            raise ValueError('The Country field must be set')
        if not username:
            raise ValueError('The Username field must be set')

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            date_of_birth=date_of_birth,
            country=country,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, date_of_birth, country, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_premium', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(username, email, date_of_birth, country, password, **extra_fields)