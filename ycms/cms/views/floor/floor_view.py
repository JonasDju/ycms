# /views/floor/floor_view.py

from django.views.generic import TemplateView


class FloorView(TemplateView):
    template_name = "floor/floor.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Aktuelle Etage aus der URL-Parameter abrufen
        current_floor = self.request.GET.get("floor", 1)  # standard 1
        context["current_floor"] = int(current_floor)
        context["total_floors"] = self.get_number_of_floor()

        return context

    def get_number_of_floor(self):
        return 4
