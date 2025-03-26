from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import BasicAuthentication
from .models import Ride
from .serializers import RideSerializer
from .permissions import IsAdmin

class RideViewSet(viewsets.ModelViewSet):
    """
    viewset for listing, retrieving, and modifying Rides.
    """
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAdmin]
    authentication_classes = [BasicAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'rider__email']
    ordering_fields = ['pickup_time']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs
