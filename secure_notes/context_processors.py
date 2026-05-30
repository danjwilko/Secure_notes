from django.utils.timezone import now


def current_year(request):
    return {"current_year": now().year}
