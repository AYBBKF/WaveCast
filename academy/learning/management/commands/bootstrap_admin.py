"""Création sécurisée du premier administrateur, sans mot de passe dans le code.

Deux usages :
- interactif sur le serveur : `python manage.py createsuperuser` (recommandé) ;
- par variables d'environnement définies uniquement sur le serveur :
  ACADEMY_BOOTSTRAP_ADMIN_EMAIL et ACADEMY_BOOTSTRAP_ADMIN_PASSWORD.
  Le compte n'est créé que s'il n'existe pas encore (un mot de passe existant n'est
  jamais écrasé). Supprimez ces variables une fois connecté.

ACADEMY_DISABLE_ACCOUNTS (e-mails séparés par des virgules) désactive des comptes,
par exemple des comptes de test.
"""

import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Crée le premier administrateur à partir des variables d'environnement du serveur (si elles sont définies)."

    def handle(self, *args, **opts):
        User = get_user_model()
        email = os.environ.get("ACADEMY_BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
        password = os.environ.get("ACADEMY_BOOTSTRAP_ADMIN_PASSWORD", "")
        if email and password:
            if User.objects.filter(email__iexact=email).exists():
                self.stdout.write("Administrateur initial : le compte existe déjà, rien n'est modifié.")
            else:
                try:
                    validate_password(password)
                except ValidationError as exc:
                    self.stderr.write("Administrateur initial non créé : " + " ".join(exc.messages))
                else:
                    user = User.objects.create_superuser(username=email, email=email, password=password)
                    user.profile.full_name = "Administrateur"
                    user.profile.email_verified_at = timezone.now()
                    user.profile.save()
                    self.stdout.write(self.style.SUCCESS(f"Administrateur initial créé : {email}"))

        for raw in os.environ.get("ACADEMY_DISABLE_ACCOUNTS", "").split(","):
            target = raw.strip().lower()
            if target and User.objects.filter(email__iexact=target, is_active=True).update(is_active=False):
                self.stdout.write(f"Compte désactivé : {target}")
