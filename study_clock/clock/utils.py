from django.conf import settings
from django.core.mail import EmailMessage


def send_email_confirmation(user):
    token = user.email_confirmation_token
    verification_url = f'{settings.SITE_URL}/verify-email?token={token}'
    email_subject = 'Email Confirmation'
    email_body = f'Please confirm your email by clicking the following link: {verification_url}'

    email = EmailMessage(subject=email_subject, body=email_body, to=[user.email])
    email.send()
