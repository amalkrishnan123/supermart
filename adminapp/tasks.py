from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
@shared_task
def main_fun(email,otp):
    print(email,otp)
    try:
        subject='verification for supermarket'
        message=f'welcome to online supermarket..please verify the otp is {otp}'
        send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False
                )
    except Exception as e:
        return f"error{str(e)}"