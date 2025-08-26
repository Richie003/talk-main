import inflect
from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from typing import Dict, Any


def custom_response(status_mthd, status, mssg:str, data:Dict):
    return {
            "status": status,
            "code": status_mthd,
            "message": mssg,
            "data": data,
    }


def send_email_message(subject, body, to_email):
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=False,
    )



def send_email_in_thread(subject, html_content, to_email):
    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    email.content_subtype = "html"  # Specify that the email content is HTML
    email.send(fail_silently=False)


class FormattedDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        p = inflect.engine()
        formatted_date = str(p.ordinal(value.day)) + " " + value.strftime("%B, %Y, %I:%M %p")
        return formatted_date
    

def format_ordinal_date(value):
    p = inflect.engine()
    formatted_date = str(p.ordinal(value.day)) + " " + value.strftime("%B, %Y, %I:%M %p")
    return formatted_date



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
