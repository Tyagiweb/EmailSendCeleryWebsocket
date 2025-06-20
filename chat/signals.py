from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Idea
from .tasks import *

@receiver(post_save, sender=Idea)
def idea_post_save(sender, instance, created, **kwargs):
    if created:
        print("Signal fired for new Idea")
        process_idea_task.delay(instance.id)
        # send_test_email()




@receiver(post_save, sender=Ticket)
def send_ticket_email(sender, instance, created, **kwargs):
    user = instance.user
    event_name = instance.event.event.event_name

    # Call async task
    send_ticket_email_task.delay(user.email, user.username, event_name, created)
