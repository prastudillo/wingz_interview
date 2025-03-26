from rest_framework import serializers
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

    class Meta:
        model = Ride
        fields = [
            'id_ride', 'status', 'rider', 'driver',
            'pickup_latitude', 'pickup_longitude',
            'dropoff_latitude', 'dropoff_longitude',
            'pickup_time'
        ]
