from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status

from .models import User, Ride, RideEvent

class RideListAPITests(APITestCase):
    def setUp(self):
        # Create an admin user and a non-admin user
        self.admin_user = User.objects.create_user(
            username='admin@example.com',
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            password='adminpass',
            role='admin'
        )
        self.non_admin_user = User.objects.create_user(
            username='user@example.com',
            first_name='Regular',
            last_name='User',
            email='user@example.com',
            password='userpass',
            role='user'
        )

        now = timezone.now()

        # Ride 1 with two ride events: one within the last 24 hours and one older than 24 hours.
        self.ride1 = Ride.objects.create(
            status='pickup',
            rider=self.non_admin_user,
            driver=self.admin_user,
            pickup_latitude=10.0,
            pickup_longitude=10.0,
            dropoff_latitude=20.0,
            dropoff_longitude=20.0,
            pickup_time=now - timedelta(hours=2),
        )
        # RideEvent within last 24 hours
        RideEvent.objects.create(
            ride=self.ride1,
            description='Status changed to pickup',
            created_at=now - timedelta(hours=12)
        )
        # RideEvent older than 24 hours
        RideEvent.objects.create(
            ride=self.ride1,
            description='Status changed to dropoff',
            created_at=now - timedelta(days=2)
        )

        # Ride 2 with one ride event within 24 hours.
        self.ride2 = Ride.objects.create(
            status='en-route',
            rider=self.non_admin_user,
            driver=self.admin_user,
            pickup_latitude=30.0,
            pickup_longitude=30.0,
            dropoff_latitude=40.0,
            dropoff_longitude=40.0,
            pickup_time=now - timedelta(hours=3),
        )
        RideEvent.objects.create(
            ride=self.ride2,
            description='Status changed to pickup',
            created_at=now - timedelta(hours=3)
        )

        self.list_url = reverse('ride-list')

    def test_permission_required(self):
        """Ensure that unauthenticated requests are denied."""
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_user_forbidden(self):
        """Ensure that non-admin users cannot access the Ride List API."""
        self.client.force_authenticate(user=self.non_admin_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
