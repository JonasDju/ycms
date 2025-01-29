import logging

from hospitool.cms.models.timetravel_manager import request_signal

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class TimetravelMiddleware:
    """
    Middleware class that performs "timetravelling". If no "time" parameter is included in the request,
    no action is taken. If the parameter is present, the request object is stored in a local thread for use
    by the :class:`~hospitool.cms.models.timetravel_manager.TimetravelManager`.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware for the current view

        :param get_response: A callable to get the response for the current request
        :type get_response: ~collections.abc.Callable
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Call the middleware for the current request

        :param request: Django request
        :type request: ~django.http.HttpRequest

        :return: The response
        :rtype: ~django.http.HttpResponse
        """
        if time := request.GET.get("time"):
            logger.info("Timetravelling to %s", time)
            request_signal.send(sender=self, request=request)
        else:
            request_signal.send(sender=self, request=None)
        response = self.get_response(request)

        return response
