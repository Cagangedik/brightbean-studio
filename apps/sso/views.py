"""SSO launch endpoint.

GET /sso/launch?ticket=<jwt>
  → verify the ticket from the Benerits admin panel
  → JIT-provision user + shared org + per-app workspace + membership
  → log the user into a Django session
  → redirect into that workspace's calendar

The ticket is a one-time, 60s bearer credential carried in the URL by the
user's browser (new tab). After this handoff the user has a normal Django
session protected by Brightbean's usual auth + RBAC.
"""

import logging

from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from apps.sso.jwt_utils import TicketError, verify_ticket
from apps.sso.provisioning import provision_sso_user

logger = logging.getLogger(__name__)

# Brightbean's auth stack has two backends; pick the model backend explicitly
# so login() doesn't error on the multi-backend setup.
_LOGIN_BACKEND = "django.contrib.auth.backends.ModelBackend"


@never_cache
@require_GET
def launch(request):
    if not getattr(settings, "SSO_ENABLED", False):
        return HttpResponseBadRequest("SSO is disabled.")

    token = request.GET.get("ticket", "")
    try:
        claims = verify_ticket(token)
    except TicketError as exc:
        logger.warning("SSO ticket rejected: %s", exc)
        return HttpResponseBadRequest(f"SSO error: {exc}")

    try:
        user, workspace = provision_sso_user(
            email=claims["email"].strip().lower(),
            name=claims.get("name", ""),
            app_id=claims["app_id"],
            app_slug=claims.get("app_slug", ""),
            app_name=claims.get("app_name", ""),
            role=claims.get("role", "viewer"),
        )
    except Exception:  # noqa: BLE001
        logger.exception("SSO provisioning failed")
        return HttpResponseBadRequest("SSO provisioning failed.")

    login(request, user, backend=_LOGIN_BACKEND)

    # Land the user in this app's workspace calendar.
    try:
        target = reverse("calendar:calendar", kwargs={"workspace_id": workspace.id})
    except Exception:  # noqa: BLE001 — fall back to dashboard if route name differs
        target = f"/workspace/{workspace.id}/calendar/"
    return redirect(target)
