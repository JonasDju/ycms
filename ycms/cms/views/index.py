import logging

from django.urls import reverse_lazy
from django.views.generic.base import RedirectView

from ..constants import group_names

logger = logging.getLogger(__name__)


class UserBasedRedirectView(RedirectView):
    """
    Utility view for redirecting users to their most sensible "home" view
    """

    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        """
        Overwrites :meth:`~django.views.generic.base.RedirectView.get_redirect_url`
        to return a redirect based on the user's primary group.

        :return: Redirect to the user's default view
        :rtype: ~django.http.HttpResponseRedirect
        """
        default_url = group_names.DEFAULT_VIEWS.get(
            str(self.request.user.group), "cms:protected:home"
        )
        return reverse_lazy(default_url)
