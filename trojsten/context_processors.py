from django.conf import settings
from trojsten import version

def current_site(request):
    return {
        'SITE': settings.SITES[settings.SITE_ID],
        'OTHER_SITES': [settings.SITES[k] for k in settings.NAVBAR_SITES],
    }

def version_string(request):
    return {
        'VERSION': version.version_string,
    }
