"""Création sécurisée du premier administrateur, sans mot de passe dans le code.

Trois usages :
- interactif sur le serveur : `python manage.py createsuperuser` ;
- promotion d'un compte créé normalement sur le site : définir seulement
  ACADEMY_BOOTSTRAP_ADMIN_EMAIL sur le serveur puis redémarrer. Le mot de passe
  n'a jamais quitté le navigateur de son propriétaire (méthode recommandée) ;
- création : ACADEMY_BOOTSTRAP_ADMIN_EMAIL et ACADEMY_BOOTSTRAP_ADMIN_PASSWORD.
  Un mot de passe existant n'est jamais écrasé.
Supprimez ces variables une fois connecté.

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
        existing = User.objects.filter(email__iexact=email).first() if email else None
        if existing:
            if existing.is_staff and existing.is_superuser:
                self.stdout.write("Administrateur initial : le compte est déjà administrateur.")
            else:
                existing.is_staff = existing.is_superuser = True
                existing.save(update_fields=["is_staff", "is_superuser"])
                self.stdout.write(self.style.SUCCESS(f"Compte promu administrateur : {email}"))
        elif email and password:
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
