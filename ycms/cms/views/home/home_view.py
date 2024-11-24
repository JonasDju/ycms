from django.views.generic import TemplateView
from ...models import Ward


class HomeView(TemplateView):
    template_name = "home/home.html"

    def get_all_patient_genders(self):
        """
        Aggregates the gender distribution of patients across all wards.

        :return: A dictionary with the total count of each gender across all wards.
        :rtype: dict[str, int]
        """
        total_gender_distribution = {
            "female_patients": 0,
            "male_patients": 0,
            "divers_patients": 0,
        }

        # Iteriere durch alle Wards
        for ward in Ward.objects.all():
            ward_genders = ward.patient_genders  # Dictionary mit den Geschlechtern
            total_gender_distribution["female_patients"] += ward_genders.get("f", 0)
            total_gender_distribution["male_patients"] += ward_genders.get("m", 0)
            total_gender_distribution["divers_patients"] += ward_genders.get("d", 0)

        return total_gender_distribution



    def get_context_data(self, **kwargs):
        """
        Extends the context data to include the aggregated gender distribution.
        """
        context = super().get_context_data(**kwargs)
        context['total_patient_genders'] = self.get_all_patient_genders()
        return context
