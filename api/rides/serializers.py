from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Ride, User, RideEvent

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'role']


class RideEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideEvent
        fields = ['id_ride_event', 'description', 'created_at']


class RideSerializer(serializers.ModelSerializer):
    rider = UserSerializer()
    driver = UserSerializer()
    todays_ride_events = serializers.SerializerMethodField()

    class Meta:
        model = Ride
        fields = [
            'id_ride', 'status', 'rider', 'driver',
            'pickup_latitude', 'pickup_longitude',
            'dropoff_latitude', 'dropoff_longitude',
            'pickup_time', 'todays_ride_events'
        ]

    def get_todays_ride_events(self, obj):
        if hasattr(obj, 'todays_events'):
            return RideEventSerializer(obj.todays_events, many=True).data
        last_24_hours = timezone.now() - timedelta(days=1)
        events = obj.ride_events.filter(created_at__gte=last_24_hours)
        return RideEventSerializer(events, many=True).data