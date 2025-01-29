from django.shortcuts import redirect


def change_theme(request, **kwargs):
    """
    Change theme
    """
    if "is_dark_theme" in request.session:
        request.session["is_dark_theme"] = not request.session["is_dark_theme"]
    else:
        request.session["is_dark_theme"] = True
    return redirect(request.META.get("HTTP_REFERER", "/"))
