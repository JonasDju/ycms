"""
Utility view for fetching existing model data during patient intake
"""
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from ...constants import days_of_week
from ...models import Ward


def fetch_ward_allowed_discharge_days(request):
    """
    Function to fetch the allowed discharge days of a ward

    :param request: The current request submitting the form
    :type request: ~django.http.HttpRequest

    :return: JSON object containing the ward's allowed discharge days
    :rtype: str
    """
    query = request.GET.get("q", "")

    try:
        ward = Ward.objects.get(pk=query)

        # return static response for now
        mask = ward.allowed_discharge_days
        if mask == 0:
            info_string = "No days allowed for discharge."
        else:
            allowed_days = [
                day
                for mask_idx, day in enumerate(days_of_week.WEEKDAYS_SHORT)
                if (mask >> mask_idx) & 0b1
            ]
            info_string = "Discharges allowed on {}.".format(",".join(allowed_days))

        return JsonResponse(
            {
                "mask": mask,
                "info_text": info_string,
                "localized_weekdays": days_of_week.WEEKDAYS_LONG,
            }
        )
    except Ward.DoesNotExist:
        return JsonResponse({})
