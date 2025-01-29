from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse


def switch_language(request, language_code):
    """
    view to switch language
    """
    if (next_page := request.META.get("HTTP_REFERER")) is None:
        next_page = reverse("cms:protected:index")

    response = HttpResponseRedirect(next_page)
    if language_code in [lang[0] for lang in settings.LANGUAGES]:
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language_code)
    return response
