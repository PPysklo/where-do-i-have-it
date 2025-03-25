from django.conf import settings


def export_version(request):
    return {
        'VERSION': settings.VERSION
    }