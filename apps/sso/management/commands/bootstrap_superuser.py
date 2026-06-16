"""Idempotently create/promote a superuser from environment variables.

Reads BOOTSTRAP_SUPERUSER_EMAIL (+ optional BOOTSTRAP_SUPERUSER_PASSWORD).
Safe to run on every deploy: if the user exists it is promoted to staff +
superuser and (when a password is given) its password is reset; if it does
not exist it is created. Does nothing when the email env var is unset.

This exists because there is no shell/SSH access to the container, so the
first admin must be provisioned through the deploy pipeline.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or promote a superuser from BOOTSTRAP_SUPERUSER_* env vars."

    def handle(self, *args, **options):
        email = (os.environ.get("BOOTSTRAP_SUPERUSER_EMAIL") or "").strip().lower()
        if not email:
            self.stdout.write("BOOTSTRAP_SUPERUSER_EMAIL not set — skipping.")
            return

        password = os.environ.get("BOOTSTRAP_SUPERUSER_PASSWORD") or ""
        User = get_user_model()

        user = User.objects.filter(email=email).first()
        created = user is None
        if created:
            user = User(email=email)

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        if password:
            user.set_password(password)
        elif created:
            # No password supplied for a brand-new user — set an unusable one
            # so the account can't be logged into until a password is set.
            user.set_unusable_password()
        user.save()

        verb = "Created" if created else "Promoted"
        self.stdout.write(self.style.SUCCESS(f"{verb} superuser {email}"))
