from .models import SiteSettings


def platform(request):
    return {"site": SiteSettings.load()}
