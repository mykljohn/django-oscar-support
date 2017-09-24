import functools
import itertools

from six.moves import map

from django.contrib import auth
from oscar.core.loading import get_model, get_class
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from oscar_support.api import serializers   # permissions


__all__ = (
    'TicketList', 'TicketDetail',
)

Ticket = get_model('oscar_support', 'Ticket')


class TicketList(generics.ListAPIView):
    queryset = Ticket.objects.all()
    serializer_class = serializers.TicketLinkSerializer


class TicketDetail(generics.RetrieveAPIView):
    queryset = Ticket.objects.all()
    serializer_class = serializers.TicketSerializer
