from ..cms.models import Ward, Floor

def global_context(request):
    """
    GLobal context processor
    """
    return {"floor_count": Floor.objects.count(), "ward_count": Ward.objects.count()}