import base64
import hashlib
import hmac
import json
import time

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.members.models import OrgMembership, WorkspaceMembership
from apps.organizations.models import Organization
from apps.sso import jwt_utils
from apps.sso.models import ExternalAppWorkspace
from apps.sso.provisioning import provision_sso_user

SECRET = "test-sso-secret-at-least-32-chars-long-xxxxx"
User = get_user_model()


@pytest.fixture(autouse=True)
def _sso_settings(settings):
    settings.BRIGHTBEAN_SSO_SECRET = SECRET
    settings.SSO_ENABLED = True
    settings.SSO_SHARED_ORG_NAME = "Benerits"


def _b64url(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_ticket(secret=SECRET, **overrides):
    now = int(time.time())
    payload = {
        "iss": "benerits-admin",
        "aud": "brightbean-studio",
        "sub": "user@benerits.com",
        "email": "user@benerits.com",
        "name": "Test User",
        "app_id": "app-uuid-1",
        "app_slug": "harmony",
        "app_name": "Harmony",
        "role": "manager",
        "jti": f"jti-{now}-{overrides.get('_n', 0)}",
        "iat": now,
        "exp": now + 60,
    }
    payload.update({k: v for k, v in overrides.items() if not k.startswith("_")})
    header = {"alg": "HS256", "typ": "JWT"}
    hb, pb = _b64url(json.dumps(header)), _b64url(json.dumps(payload))
    sig = hmac.new(secret.encode(), f"{hb}.{pb}".encode(), hashlib.sha256).digest()
    return f"{hb}.{pb}.{_b64url(sig)}"


# ---- JWT verification ----------------------------------------------------


class TestVerifyTicket:
    def test_valid(self):
        claims = jwt_utils.verify_ticket(make_ticket(_n=1))
        assert claims["email"] == "user@benerits.com"
        assert claims["app_id"] == "app-uuid-1"

    def test_replay_rejected(self):
        t = make_ticket(_n=2)
        jwt_utils.verify_ticket(t)
        with pytest.raises(jwt_utils.TicketError):
            jwt_utils.verify_ticket(t)

    def test_bad_signature(self):
        t = make_ticket(secret="x" * 40, _n=3)
        with pytest.raises(jwt_utils.TicketError):
            jwt_utils.verify_ticket(t)

    def test_expired(self):
        now = int(time.time())
        t = make_ticket(_n=4, iat=now - 120, exp=now - 60)
        with pytest.raises(jwt_utils.TicketError):
            jwt_utils.verify_ticket(t)

    def test_wrong_audience(self):
        with pytest.raises(jwt_utils.TicketError):
            jwt_utils.verify_ticket(make_ticket(_n=5, aud="nope"))

    def test_wrong_issuer(self):
        with pytest.raises(jwt_utils.TicketError):
            jwt_utils.verify_ticket(make_ticket(_n=6, iss="evil"))

    def test_malformed(self):
        with pytest.raises(jwt_utils.TicketError):
            jwt_utils.verify_ticket("not.a.jwt.at.all")


# ---- Provisioning --------------------------------------------------------


@pytest.mark.django_db
class TestProvisioning:
    def test_creates_user_org_workspace_membership(self):
        user, ws = provision_sso_user(
            email="a@benerits.com", name="A", app_id="app-1",
            app_slug="harmony", app_name="Harmony", role="manager",
        )
        assert user.email == "a@benerits.com"
        org = Organization.objects.get(name="Benerits")
        # User belongs ONLY to the shared org (auto "My Organization" cleaned up).
        assert list(
            OrgMembership.objects.filter(user=user).values_list("organization__name", flat=True)
        ) == ["Benerits"]
        assert ws.organization_id == org.id
        wm = WorkspaceMembership.objects.get(user=user, workspace=ws)
        assert wm.workspace_role == "manager"
        assert ExternalAppWorkspace.objects.get(external_app_id="app-1").workspace_id == ws.id

    def test_idempotent_same_app_same_workspace(self):
        u1, ws1 = provision_sso_user(email="b@benerits.com", name="B", app_id="app-2", app_slug="x", app_name="X", role="manager")
        u2, ws2 = provision_sso_user(email="b@benerits.com", name="B", app_id="app-2", app_slug="x", app_name="X", role="manager")
        assert u1.id == u2.id
        assert ws1.id == ws2.id
        assert WorkspaceMembership.objects.filter(user=u1, workspace=ws1).count() == 1

    def test_different_apps_get_different_workspaces(self):
        _, ws_a = provision_sso_user(email="c@benerits.com", name="C", app_id="app-A", app_slug="a", app_name="A", role="manager")
        _, ws_b = provision_sso_user(email="c@benerits.com", name="C", app_id="app-B", app_slug="b", app_name="B", role="viewer")
        assert ws_a.id != ws_b.id
        assert ws_a.organization_id == ws_b.organization_id

    def test_role_clamped_to_viewer_for_unknown(self):
        user, ws = provision_sso_user(email="d@benerits.com", name="D", app_id="app-3", app_slug="x", app_name="X", role="superadmin")
        assert WorkspaceMembership.objects.get(user=user, workspace=ws).workspace_role == "viewer"


# ---- Launch view ---------------------------------------------------------


@pytest.mark.django_db
class TestLaunchView:
    def test_valid_ticket_logs_in_and_redirects(self, client):
        resp = client.get(reverse("sso:launch"), {"ticket": make_ticket(_n=10, email="e@benerits.com")})
        assert resp.status_code == 302
        assert "/calendar/" in resp["Location"]
        assert client.session.get("_auth_user_id")

    def test_missing_ticket_400(self, client):
        resp = client.get(reverse("sso:launch"))
        assert resp.status_code == 400

    def test_replayed_ticket_rejected(self, client, django_user_model):
        # A replayed ticket must never produce a fresh login. We use a second,
        # clean client to model the replay coming from elsewhere (the first
        # client is already authenticated, so its own re-request would just hit
        # the post-login flow rather than re-running ticket verification).
        from django.test import Client

        t = make_ticket(_n=11, email="f@benerits.com")
        first = client.get(reverse("sso:launch"), {"ticket": t})
        assert first.status_code == 302  # legitimate first use

        attacker = Client()
        replay = attacker.get(reverse("sso:launch"), {"ticket": t})
        assert replay.status_code == 400  # jti already consumed
        assert not attacker.session.get("_auth_user_id")  # no session minted

    def test_disabled_400(self, client, settings):
        settings.SSO_ENABLED = False
        resp = client.get(reverse("sso:launch"), {"ticket": make_ticket(_n=12)})
        assert resp.status_code == 400
