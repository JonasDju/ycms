from django.views.generic import TemplateView

from ...models import Floor, Ward


class FloorView(TemplateView):
    template_name = "floor/floor.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Hol die aktuelle Etage
        current_floor_order = self.request.GET.get("floor", None)
        if current_floor_order:
            current_floor = Floor.objects.filter(order=current_floor_order).first()
        else:
            current_floor = Floor.objects.first()
        current_floor_id = current_floor.id if current_floor else None

        # Bereite Daten vor
        context["current_floor"] = current_floor
        sorted_floors = sorted(Floor.objects.all(), key=lambda x: x.order, reverse=True)
        context["floors"] = sorted_floors

        # Berechne den nächsten Etagen-Order
        index = sorted_floors.index(current_floor) if current_floor is not None else None
        next = sorted_floors[index - 1] if index is not None and index > 0 else None
        prev = sorted_floors[index + 1] if index is not None and index < len(sorted_floors) - 1 else None
        context["next_floor_name"] = next
        context["prev_floor_name"] = prev

        # Get wards for the selected floor
        context["floor_wards"] = (
            Ward.objects.filter(floor=current_floor_id) if current_floor_id else []
        )

        return context
