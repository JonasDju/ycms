def theme(request):
    """
    Theme context processor
    """
    if "is_dark_theme" in request.session:
        is_dark_theme = request.session["is_dark_theme"]
        return {"is_dark_theme": is_dark_theme}
    return {"is_dark_theme": False}
