from django.contrib.auth.models import AbstractUser
from django.db import models

# class CustomUser(AbstractUser):
#     # Add any extra fields here if needed
#     pass


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    total_count = models.IntegerField(default=0)
    left_count = models.IntegerField(default=0)
    is_online = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 


class Idea(BaseModel):
    submitted_by   = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='submitted_ideas')
    title          = models.CharField(max_length=255)
    description    = models.TextField()

    reviwed_by     = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='reviewed_person',null=True,blank=True)
    status         = models.CharField(max_length=20,choices=[('Pending', 'Pending'),('Accepted', 'Accepted'),('Rejected', 'Rejected'),],default='Pending')
    remarks        = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.title

class Room(models.Model):
    user = models.ForeignKey(CustomUser, related_name='user_rooms', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(CustomUser, related_name='reviewer_rooms', on_delete=models.CASCADE)
    chat = models.JSONField(null=True,blank=True)

    def __str__(self):
        return str(self.id)


class Organizer(BaseModel):
    user         = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='organizer_person')
    adhar_number = models.CharField(max_length=12,null=True,blank=True)
    mobile       = models.CharField(max_length=10) 
    is_approved  = models.BooleanField(default=False)
    is_blocked   = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)


class Event(BaseModel):
    organizer     = models.ForeignKey(Organizer,on_delete=models.CASCADE,related_name='event_organizer_person')
    event_name    = models.CharField(max_length=50)
    description   = models.TextField(null=True,blank=True)
    date          = models.DateField(null=True,blank=True)
    duration      = models.CharField(max_length=50,null=True,blank=True)
    location      = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.event_name


class EventPrice(BaseModel):
    event          = models.ForeignKey(Event,on_delete=models.CASCADE,related_name='event_price')
    price          = models.CharField(max_length=20)
    description    = models.TextField(null=True,blank=True)

    def __str__(self):
        return str(self.event)   


class Ticket(BaseModel):
    user         = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='user_ticket')
    event        = models.ForeignKey(EventPrice,on_delete=models.CASCADE,related_name='event_book')
    is_paid      = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False) 

    def __str__(self):
        return str(self.user)         