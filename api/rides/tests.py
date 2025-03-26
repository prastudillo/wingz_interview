from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from django.db import connection
from django.test.utils import CaptureQueriesContext

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

        # Create Ride 1 with two ride events:
        # one within the last 24 hours and one older than 24 hours.
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

        # Create Ride 2 with one ride event within 24 hours.
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

    def test_list_rides(self):
        """Test that the API returns rides with the correct structure and filtering of ride events."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 2)

        # Verify that for ride1, only events within the last 24 hours are returned
        for ride in data['results']:
            if ride['id_ride'] == self.ride1.id_ride:
                self.assertEqual(len(ride['todays_ride_events']), 1)
            elif ride['id_ride'] == self.ride2.id_ride:
                self.assertEqual(len(ride['todays_ride_events']), 1)

    def test_filtering_by_status_and_rider_email(self):
        """Test filtering rides by status and rider email."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {'status': 'pickup'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['status'], 'pickup')

        response = self.client.get(self.list_url, {'rider__email': self.non_admin_user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['results']), 2)

    def test_sorting_by_pickup_time(self):
        """Test ordering of rides by pickup_time in ascending order."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {'ordering': 'pickup_time'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rides = response.json()['results']
        pickup_times = [ride['pickup_time'] for ride in rides]
        self.assertEqual(pickup_times, sorted(pickup_times))

    def test_sorting_by_distance(self):
        """Test that rides are sorted by computed distance when latitude and longitude are provided."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {
            'ordering': 'distance',
            'latitude': '0',
            'longitude': '0'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rides = response.json()['results']
        self.assertEqual(rides[0]['id_ride'], self.ride1.id_ride)

    def test_pagination_structure(self):
        """Test that pagination keys are present in the response."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('count', data)
        self.assertIn('next', data)
        self.assertIn('previous', data)

    def test_minimal_query_count(self):
        """Ensure that the number of DB queries is minimized (expect 2 or 3 queries, including pagination count)."""
        self.client.force_authenticate(user=self.admin_user)
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(self.list_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertLessEqual(len(queries), 3, msg=f"Too many queries executed: {len(queries)}")