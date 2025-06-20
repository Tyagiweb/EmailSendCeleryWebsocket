from celery import shared_task
from .models import *
# from django.core.mail import send_mail
# from django.conf import settings

@shared_task
def print_hello():
    print("Hello from Celery Beat!")


@shared_task
def process_idea_task(idea_id):
    try:
        idea = Idea.objects.get(id=idea_id)
        reviewers = CustomUser.objects.filter(
            groups__name='Reviewer',
            is_online=True
        ).order_by('left_count') 

        if not reviewers.exists():
            print("No online reviewers available")
            return

        assigned_reviewer = reviewers.first()
        idea.reviwed_by = assigned_reviewer

        assigned_reviewer.left_count += 1
        assigned_reviewer.save()
        idea.save()
    except Idea.DoesNotExist:
        print(f"Idea with id {idea_id} not found")

from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_ticket_email_task(user_email, username, event_name, created):
    if created:
        subject = f'Ticket Booking Confirmed: {event_name}'
        message = f'Hello ,\n\nYour ticket for "{event_name}" has been successfully booked.'
    else:
        subject = f'Ticket Updated: {event_name}'
        message = f'Hello ,\n\nYour ticket for "{event_name}" has been updated.'

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )      