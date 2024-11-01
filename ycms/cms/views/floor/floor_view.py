# /views/floor/floor_view.py

from django.views.generic import TemplateView


class FloorView(TemplateView):
    template_name = "floor/floor.html"

    def get_context_data(self, **kwargs):
        # Rufe den Kontext der übergeordneten Klasse ab
        context = super().get_context_data(**kwargs)

        # Füge die aktuelle Etage hinzu
        context[
            "current_floor"
        ] = 3  # Ersetze dies durch die tatsächliche Logik zur Bestimmung der Etage
        return context
