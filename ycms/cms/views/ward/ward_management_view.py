import json
from django.db import transaction
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect

from ...constants import bed_types, job_types
from ...decorators import permission_required
from ...forms import WardForm
from ...models import Bed, Room, User, Ward


@method_decorator(permission_required("cms.add_ward"), name="dispatch")
class WardManagementView(TemplateView):
    """
    View to see all wards data and add a new one
    """

    template_name = "ward/ward_management.html"

    def get(self, request, *args, **kwargs):
        r"""
        This function returns a list of all wards,
        as well as a form for creating a new one

        :param request: The current request
        :type request: ~django.http.HttpRequest

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict


        :return: List of all wards
        :rtype: ~django.template.response.TemplateResponse
        """
        ward_form = WardForm()

        return render(
            request,
            self.template_name,
            {
                "ward_form": ward_form,
                "bed_types": bed_types.CHOICES,
                **self._get_ward_info(),
                **super().get_context_data(**kwargs),
            },
        )

    @staticmethod
    def _get_ward_info():
        wards = Ward.objects.all().order_by('id')
        return {
            "wards": wards,
            "wards_count": wards.count(),
            "beds_count": sum(ward.total_beds for ward in wards),
            "occupied_beds": sum(ward.occupied_beds for ward in wards),
            "available_beds": sum(ward.available_beds for ward in wards),
            "doctors_count": User.objects.filter(job_type=job_types.DOCTOR).count(),
            "nurses_count": User.objects.filter(job_type=job_types.NURSE).count(),
        }

    def post(self, request, *args, **kwargs):
        r"""

        :param request: The current request
        :type request: ~django.http.HttpRequest

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict

        :return: Redirect to list of wards
        :rtype: ~django.http.HttpResponseRedirect
        """
        ward_form = WardForm(
            data=request.POST, additional_instance_attributes={"creator": request.user}
        )
        if not ward_form.is_valid():
            ward_form.add_error_messages(request)
            return render(
                request,
                self.template_name,
                {
                    "ward_form": ward_form,
                    **self._get_ward_info(),
                    **super().get_context_data(**kwargs),
                },
            )
        ward = ward_form.save()
        messages.success(
            request, _('Addition of new ward "{}" successful!').format(ward.name)
        )

        if not (room_dict := request.POST.get("rooms")):
            return redirect("cms:protected:ward_management")

        room_counter = 0
        bed_counter = 0
        for room_number, beds in json.loads(room_dict).items():
            room = Room.objects.create(
                ward=ward, creator=request.user, room_number=room_number
            )
            room_counter += 1
            for bed_type in beds:
                bed_counter += 1
                Bed.objects.create(room=room, creator=request.user, bed_type=bed_type)

        messages.success(
            request,
            _('Added {} rooms with {} beds to "{}".').format(
                room_counter, bed_counter, ward.name
            ),
        )
        return redirect("cms:protected:ward_management")


@method_decorator(permission_required("cms.delete_ward"), name="dispatch")
class WardDeleteView(DeleteView):
    """
    View to delete a ward 
    """

    model = Ward
    success_url = reverse_lazy("cms:protected:ward_management")

    def form_valid(self, form):
        messages.success(self.request, _("The ward has been deleted."))
        return super().form_valid(form)

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return redirect("cms:protected:ward_management")


@method_decorator(permission_required("cms.edit_ward"), name="dispatch")
class WardEditView(UpdateView):
    """
    View to edit ward information
    """

    model = Ward
    form_class = WardForm
    # success_url = reverse_lazy("cms:protected:ward_management")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"prefix": self.kwargs["pk"]})
        return kwargs

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))

    def form_valid(self, form):
        if room_dict := self.request.POST.get("rooms"):
            try:
                with transaction.atomic():
                    ward = form.save()
                    room_counter = 0
                    bed_counter = 0
                    duplicate_rooms = []
                    
                    for room_number, beds in json.loads(room_dict).items():
                        # Check if room number already exists
                        if ward.rooms.filter(room_number=room_number).exists():
                            duplicate_rooms.append(room_number)
                
                    if duplicate_rooms:
                        messages.error(
                            self.request,
                            _('The following room numbers already exist: {}').format(
                                ', '.join(str(num) for num in duplicate_rooms)
                            ),
                        )
                        # Raise exception to rollback transaction
                        raise ValueError("Duplicate room numbers found")
                    
                    for room_number, beds in json.loads(room_dict).items():
                        room = Room.objects.create(
                            ward=ward,
                            creator=self.request.user,
                            room_number=room_number
                        )
                        room_counter += 1
                        for bed_type in beds:
                            bed_counter += 1
                            Bed.objects.create(room=room, creator=self.request.user, bed_type=bed_type)
                    
                    if room_counter > 0:
                        messages.success(
                            self.request,
                            _('Added {} new rooms with {} new beds to the ward.').format(
                                room_counter, bed_counter
                            ),
                        )
                    messages.success(
                        self.request, _("Ward information has been successfully updated!")
                    )
                    
            except ValueError:
                # Return to the same page without saving anything
                return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))
        else:
            # If no rooms to add, just save the ward information
            ward = form.save()
            messages.success(
                self.request, _("Ward information has been successfully updated!")
            )
        
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))
