"""Connexion par adresse e-mail (insensible à la casse), via le système d'authentification Django."""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = (username or kwargs.get("email") or "").strip()
        if not email or password is None:
            return None
        User = get_user_model()
        user = User.objects.filter(email__iexact=email).order_by("id").first()
        if user is None:
            # Même coût de calcul qu'un vrai essai, pour ne pas révéler si le compte existe.
            User().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
