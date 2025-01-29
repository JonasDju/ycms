import logging
import threading
from datetime import timedelta

from django.core.exceptions import FieldError
from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_datetime

_thread_locals = threading.local()
request_signal = models.signals.Signal()
logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class TimetravelManager(models.Manager):
    """
    This manager filters querysets by time, if the corresponding GET parameter was specified in the request.
    """

    def get_queryset(self):
        """
        Get the queryset, filtered by time if the parameter was specified in the request.

        :return: The queryset
        """
        queryset = super().get_queryset()

        request = _thread_locals.request if hasattr(_thread_locals, "request") else None
        if not (request and request.GET.get("time")):
            return queryset

        time = current_or_travelled_time()
        timetravel_filters = [
            "created_at__lte",
            "admission_date__lte",
            "discharge_date__gt",
        ]
        for field in timetravel_filters:
            try:
                queryset = queryset.filter(**{field: time})
            except FieldError:
                pass
        return queryset


def current_or_travelled_time():
    """
    Helper function to return a mocked current time
    whenever we are timetravelling
    """
    try:
        return parse_datetime(_thread_locals.request.GET["time"]) - timedelta(hours=1)
    except AttributeError:
        return timezone.now()


def set_request(**kwargs):
    """
    Helper function for setting the request
    object once a signal is received
    """
    _thread_locals.request = kwargs["request"]


request_signal.connect(set_request)
