import logging

from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView, UpdateView, DeleteView, CreateView
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.db import transaction
from ...models import Ward, Room, Bed, User
from ...forms import WardForm, RoomForm, BedForm, IntakeBedAssignmentForm, PatientForm

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
        pk = kwargs.get("pk")
        try:
            ward = Ward.objects.get(id=pk)
            rooms = [
                (
                    room,
                    [
                        (
                            patient,
                            PatientForm(instance=patient),
                            IntakeBedAssignmentForm(instance=patient.current_stay),
                        )
                        for patient in room.patients()
                    ],
                )
                for room in ward.rooms.all()
            ]
        except Ward.DoesNotExist:
            rooms = []
            ward = None
            unassigned_bed_assignments = []
            patient_info = {}
            wards = []

        return {
            "ward": ward,
            "rooms": rooms,
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
    

@method_decorator(permission_required("cms.add_ward"), name="dispatch")
class RoomDeleteView(DeleteView):
    """
    View to delete a room
    """
    model = Room

    def form_valid(self, _form):
        # Check if any bed in the room is not available
        beds = self.object.beds.all()
        if any(not bed.is_available for bed in beds):
            messages.error(self.request, _("The room cannot be deleted because it contains unavailable beds."))
        else:
            self.object.delete()
            messages.success(self.request, _("The room has beed deleted."))
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))


    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))



@method_decorator(permission_required("cms.add_ward"), name="dispatch")
class BedUpdateView(UpdateView):
    """
    View to update a bed
    """
    model = Bed
    form_class = BedForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Bed updated successfully"))
        return super().form_valid(form)
    
    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))

    def get_success_url(self):
        return reverse_lazy("cms:protected:ward_details", kwargs={"pk": self.object.room.ward.id})
    

@method_decorator(permission_required("cms.add_ward"), name="dispatch")
class BedDeleteView(DeleteView):
    """
    View to delete a bed
    """
    model = Bed

    def form_valid(self, _form):
        # Check if the bed is not available
        if not self.object.is_available:
            messages.error(self.request, _("The bed cannot be deleted because it is not available."))
        else:
            self.object.delete()
            messages.success(self.request, _("The bed has beed deleted."))   
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))
    

@method_decorator(permission_required("cms.add_ward"), name="dispatch")
class BedCreateView(CreateView):
    """
    View to create a bed
    """
    model = Bed
    success_url = reverse_lazy("cms:protected:ward_details")
    form_class = BedForm

    def form_valid(self, form):
        room_id = self.kwargs.get('pk')
        room = get_object_or_404(Room, id=room_id)
        form.instance.room = room
        form.instance.creator = self.request.user
        form.save()
        messages.success(self.request, _("Bed created successfully"))
        return super().form_valid(form)
    
    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))

    def get_success_url(self):
        return reverse_lazy("cms:protected:ward_details", kwargs={"pk": self.object.room.ward.id})