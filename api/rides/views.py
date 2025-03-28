from datetime import timedelta

from django.db.models import ExpressionWrapper, F, FloatField, Prefetch
from django.db.models.functions import Power
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.authentication import BasicAuthentication

from .models import Ride, RideEvent, User
from .permissions import IsAdmin
from .serializers import RideSerializer, RideEventSerializer, UserSerializer


class RideViewSet(viewsets.ModelViewSet):
    """
    Viewset for listing, retrieving, and modifying Rides.
    """

    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAdmin]
    authentication_classes = [BasicAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "rider__email"]
    ordering_fields = ["pickup_time"]

    def get_queryset(self):
        qs = super().get_queryset().select_related("rider", "driver")
        # Prefetch ride events from the last 24 hours.
        last_24_hours = timezone.now() - timedelta(days=1)
        qs = qs.prefetch_related(
            Prefetch(
                "ride_events",
                queryset=RideEvent.objects.filter(created_at__gte=last_24_hours),
                to_attr="todays_events",
            )
        )

        # If user wants to sort by distance:
        request = self.request
        ordering_param = request.query_params.get("ordering", "")
        latitude = request.query_params.get("latitude")
        longitude = request.query_params.get("longitude")
        if latitude and longitude and "distance" in ordering_param:
            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except ValueError:
                pass
            else:
                distance_expr = ExpressionWrapper(
                    Power(F("pickup_latitude") - latitude, 2)
                    + Power(F("pickup_longitude") - longitude, 2),
                    output_field=FloatField(),
                )
                qs = qs.annotate(distance=distance_expr)
                if ordering_param.startswith("-"):
                    qs = qs.order_by(F("distance").desc(nulls_last=True))
                else:
                    qs = qs.order_by("distance")

        return qs


class RideEventViewSet(viewsets.ModelViewSet):
    """
    Viewset for listing, retrieving, and modifying RideEvents.
    """

    queryset = RideEvent.objects.all()
    serializer_class = RideEventSerializer
    permission_classes = [IsAdmin]
    authentication_classes = [BasicAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["ride__id_ride", "description"]
    ordering_fields = ["created_at"]


class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset for listing, retrieving, and modifying Users.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    authentication_classes = [BasicAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["username", "email", "role"]
    ordering_fields = ["first_name", "last_name", "email"]
