from django.views.generic import TemplateView


class FloorView(TemplateView):
    template_name = "floor/floor.html"
    floor = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Aktuelle Etage aus der URL-Parameter abrufen
        current_floor = self.request.GET.get(
            "floor", 1
        )  # Standardwert 1, wenn nicht gesetzt
        context["current_floor"] = int(current_floor)
        context["total_floors"] = self.get_number_of_floor()  # Anzahl der Etagen
        context["upper_bound_floor"] = self.floor - 1

        # Erstelle eine Liste der Etagen und kehre sie um
        context["floors"] = list(reversed(range(0, context["total_floors"])))

        return context

    def get_number_of_floor(self):
        return self.floor  # Gibt die Anzahl der Etagen zurück
