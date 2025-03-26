from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    role = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.username


class Ride(models.Model):
    id_ride = models.AutoField(primary_key=True)
    status = models.CharField(max_length=50)
    rider = models.ForeignKey(User, related_name='rides_as_rider', on_delete=models.CASCADE, db_column='id_rider')
    driver = models.ForeignKey(User, related_name='rides_as_driver', on_delete=models.CASCADE, db_column='id_driver')
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField()

    objects = models.Manager()

    def __str__(self):
        return f"Ride {self.id_ride} - {self.status}"


class RideEvent(models.Model):
    id_ride_event = models.AutoField(primary_key=True)
    ride = models.ForeignKey(Ride, related_name='ride_events', on_delete=models.CASCADE, db_column='id_ride')
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    objects = models.Manager()

    def __str__(self):
        return f"RideEvent {self.id_ride_event} for Ride {self.ride.id_ride}"
