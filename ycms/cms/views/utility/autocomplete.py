"""
Utility views for autocompleting various user inputs
"""
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound

from ...models import ICD10Entry, Patient


def autocomplete_icd10(request):
    """
    Function to autocomplete search queries for ICD-10-GM codes or descriptions

    :param request: The current request submitting the form
    :type request: ~django.http.HttpRequest

    :return: JSON object containing search results
    :rtype: str
    """
    query = request.GET.get("q", "")
    results = ICD10Entry.objects.filter(
        Q(code__icontains=query) | Q(description__icontains=query)
    )[:15]
    return JsonResponse(
        {
            "suggestions": [
                {"id": result.id, "name": f"{result.code} --- {result.description}"}
                for result in results
            ]
        }
    )


def autocomplete_patient(request):
    """
    Function to autocomplete search queries for patients.
    If query field q is given, returns all patients where lastname, firstname or date of birth matches.
    Otherwise returns patients where fields lastName, firstName and dateOfBirth all match.

    :param request: The current request submitting the form
    :type request: ~django.http.HttpRequest

    :return: JSON object containing search results
    :rtype: str
    """
    if query := request.GET.get("q", ""):
        results = Patient.objects.filter(
            Q(last_name__icontains=query)
            | Q(first_name__icontains=query)
            | Q(date_of_birth__icontains=query)
        )[:15]

        return JsonResponse({
            "suggestions": [
                {
                    "id": result.id,
                    "name": f"{result.last_name}, {result.first_name}, {result.date_of_birth}",
                }
                for result in results
            ]    
        })
    
    else:
        lastNameQuery = request.GET.get("lastName", "")
        firstNameQuery = request.GET.get("firstName", "")
        dateQuery = request.GET.get("dateOfBirth", "")

        results = Patient.objects.filter(
            Q(last_name__icontains=lastNameQuery)
            & Q(first_name__icontains=firstNameQuery)
            & Q(date_of_birth__icontains=dateQuery)
        )

        return JsonResponse({
            "num_results": results.count(),
            "results": [
                {
                    "id": patient.id,
                    "name": f"{patient.last_name}, {patient.first_name}, {patient.date_of_birth}",
                }
                for patient in results[:15]
            ]
        })

def fetch_patient(request):
    """
    Function to fetch the details about an existing patient

    :param request: The current request submitting the form
    :type request: ~django.http.HttpRequest

    :return: JSON object containing the patient's details
    :rtype: str
    """
    query = request.GET.get("q", "")

    try:
        patient = Patient.objects.get(pk=query)

        return JsonResponse(
            {
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "gender": patient.gender,
                "date_of_birth": patient.date_of_birth,
                "insurance_type": patient.insurance_type,
            }
        )
    except Patient.DoesNotExist:
        return HttpResponseNotFound(f"No patient with id {query} found.")
