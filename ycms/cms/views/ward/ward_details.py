import logging

from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.db import transaction
from ...models import Ward, Room, Bed, User
from ...forms import WardForm, RoomForm, BedForm

from ...constants import bed_types

logger = logging.getLogger(__name__)

@method_decorator(permission_required("cms.view_ward"), name="dispatch")
class WardDetailsView(TemplateView):
    """
    View to see all information about a single ward
    and its rooms and beds
    """
    template_name = "ward/ward_details.html"

    def get_context_data(self, **kwargs):
        """
        This function returns all data about a ward.

        :param kwargs: The supplied keyword arguments
        :type kwargs: dict

        :return: Response for filtered offers
        :rtype: ~django.template.response.TemplateResponse
        """
        ward = get_object_or_404(Ward, pk=kwargs["pk"])
        return {
            "ward": ward,
            "bed_types": bed_types.CHOICES,
            "ward_form": WardForm(instance=ward, prefix=kwargs["pk"]),
            "room_forms": {room.id: RoomForm(instance=room) for room in ward.rooms.all()},
            "bed_forms": {bed.id: BedForm(instance=bed) for bed in (Bed.objects.filter(room__ward=ward))},
            **super().get_context_data(**kwargs),
        }
    

@method_decorator(permission_required("cms.add_ward"), name="dispatch")
class RoomUpdateView(UpdateView):
    """
    View to update a room
    """
    model = Room
    form_class = RoomForm

    def form_valid(self, form):
        # check if the room number in this ward is unique
        if Room.objects.filter(room_number=form.cleaned_data["room_number"], ward=self.object.ward).exclude(pk=self.object.pk).exists():
            form.add_error("room_number", _("This room number already exists in this ward"))
            return self.form_invalid(form)
        form.save()
        messages.success(self.request, _("Room updated successfully"))
        return super().form_valid(form)
    
    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))


    def get_success_url(self):
        return reverse_lazy("cms:protected:ward_details", kwargs={"pk": self.object.ward.id})
    