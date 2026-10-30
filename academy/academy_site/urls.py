from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.static import serve

admin.site.site_header = "Flux Intelligent Academy — administration technique"
admin.site.site_title = "Flux Intelligent Academy"

urlpatterns = [
    # Administration technique Django (superutilisateurs) ; l'administration du
    # contenu au quotidien se fait dans /gestion/.
    # Sonde de santé du conteneur (sans base de données ni session).
    path("sante/", lambda request: HttpResponse("ok", content_type="text/plain")),
    path("django-admin/", admin.site.urls),
    path("", include("learning.urls")),
    # Fichiers publics téléversés (logo, couvertures, images de leçons).
    # Les certificats PDF ne sont PAS ici : ils passent par une vue contrôlée.
    path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
]
