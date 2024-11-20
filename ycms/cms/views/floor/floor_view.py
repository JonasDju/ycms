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
        dict_floor_order = {floor.order: floor.name for floor in sorted_floors}

        # Berechne den nächsten Etagen-Order
        next_floor_order = current_floor.order + 1 if current_floor else None
        prev_floor_order = current_floor.order - 1 if current_floor else None
        context["next_floor_name"] = dict_floor_order.get(next_floor_order, None)
        context["prev_floor_order"] = dict_floor_order.get(prev_floor_order, None)

        # Ab hier wollen wir weinen
        context["floor_wards"] = (
            Ward.objects.filter(floor=current_floor_id) if current_floor_id else []
        )

        return context
