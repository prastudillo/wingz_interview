import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from rides.models import Ride, RideEvent, User


class Command(BaseCommand):
    help = (
        "Clears existing rides and ride events and "
        "populates the Ride table with sample data and ride events"
    )

    def handle(self, *args, **options):
        # Clear existing rides (which cascades to ride events)
        Ride.objects.all().delete()
        self.stdout.write(self.style.WARNING("Cleared existing rides and ride events."))

        # Create or get a rider
        rider, _ = User.objects.get_or_create(
            username="rider1",
            defaults={
                "email": "rider1@example.com",
                "role": "rider",
                "password": "pass",
            },
        )
        # Create or get a driver
        driver, _ = User.objects.get_or_create(
            username="driver1",
            defaults={
                "email": "driver1@example.com",
                "role": "driver",
                "password": "pass",
            },
        )

        # Create 20 rides
        for i in range(20):
            ride = Ride.objects.create(
                status="completed",
                rider=rider,
                driver=driver,
                pickup_latitude=random.uniform(-90, 90),
                pickup_longitude=random.uniform(-180, 180),
                dropoff_latitude=random.uniform(-90, 90),
                dropoff_longitude=random.uniform(-180, 180),
                pickup_time=timezone.now() - timedelta(days=random.randint(0, 10)),
            )
            # Create two ride events for each ride:
            # A "pickup" event and a "dropoff" event with created_at set to now
            RideEvent.objects.create(
                ride=ride,
                description="Status changed to pickup",
                created_at=timezone.now(),
            )
            RideEvent.objects.create(
                ride=ride,
                description="Status changed to dropoff",
                created_at=timezone.now(),
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully created 20 rides with associated ride events."
            )
        )
