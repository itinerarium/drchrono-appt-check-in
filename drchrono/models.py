from django.db import models
import uuid
from datetime import timedelta
# Create your models here.

class GetOrNoneManager(models.Manager):
    """Adds get_or_none method to objects
    """
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None

class Visit(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor_id = models.IntegerField()
    patient_id = models.IntegerField()
    appt_id = models.CharField(max_length=1024)
    appt_time = models.DateTimeField()
    arrival_time = models.DateTimeField(auto_now_add=True)
    time_seen = models.DateTimeField(blank=True,null=True)

    objects = GetOrNoneManager()

class Kiosk(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor_id = models.IntegerField()
    refresh_token = models.CharField(max_length=24)
    access_token = models.CharField(max_length=60)
    expires_in = models.IntegerField() # seconds?
    expire_check_time = models.DateTimeField(auto_now_add=True)

    objects = GetOrNoneManager()

class Average_wait(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor_id = models.CharField(max_length=1024)
    time_sum = models.DurationField(default=0)
    visit_count = models.IntegerField(default=0)

    objects = GetOrNoneManager()
