from django.contrib.auth.models import BaseUserManager
import logging

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def create_user(self, username, email, date_of_birth, country, password, **extra_fields):
        logger.debug('Creating a user with the name: %s', username)
        if not email:
            logger.error('The email address for the user is not specified')
            raise ValueError('The Email field must be set')
        if not date_of_birth:
            logger.error('The date of birth for the user is not specified')
            raise ValueError('The Date of Birth field must be set')
        if not country:
            logger.error('The country for the user is not specified')
            raise ValueError('The Country field must be set')
        if not username:
            logger.error('The username for the user is not specified')
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
        logger.info('The user has been created: %s', username)
        return user

    def create_superuser(self, username, email, date_of_birth, country, password, **extra_fields):
        logger.debug('Creating a superuser: %s', username)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_premium', True)

        if extra_fields.get('is_staff') is not True:
            logger.error('Superuser must have is_staff=True')
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            logger.error('Superuser must have is_superuser=True')
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(username, email, date_of_birth, country, password, **extra_fields)