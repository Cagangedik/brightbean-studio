"""JIT provisioning for SSO users coming from the Benerits admin panel.

Model:
  - One shared "Benerits" Organization holds everything.
  - Each external admin app maps to one Workspace in that org (via
    ExternalAppWorkspace).
  - Each admin user becomes their own Brightbean User (looked up by email),
    added to the shared org and to the app's workspace with a mapped role.

The User ``post_save`` signal auto-creates a personal "My Organization" for
every new user. We reconcile that away (same approach as the invite-accept
flow in apps/accounts/signals.py) so SSO users live only in the shared org.
"""

from django.conf import settings
from django.db import transaction

SHARED_ORG_NAME_DEFAULT = "Benerits"

# Brightbean workspace role for each role the admin sends. The admin already
# maps its studio roles down to this vocabulary, but we clamp again defensively.
_ALLOWED_WORKSPACE_ROLES = {"owner", "manager", "editor", "contributor", "client", "viewer"}


def _shared_org_name() -> str:
    return getattr(settings, "SSO_SHARED_ORG_NAME", SHARED_ORG_NAME_DEFAULT)


def _map_workspace_role(role: str) -> str:
    from apps.members.models import WorkspaceMembership

    if role in _ALLOWED_WORKSPACE_ROLES:
        return role
    return WorkspaceMembership.WorkspaceRole.VIEWER


def get_or_create_shared_org():
    from apps.organizations.models import Organization

    org, _ = Organization.objects.get_or_create(
        name=_shared_org_name(),
        defaults={"default_timezone": "UTC"},
    )
    return org


def _cleanup_auto_provisioned_org(user, keep_org):
    """Remove the personal 'My Organization' the post_save signal created.

    Mirrors apps/accounts/signals.py: only delete an org named
    'My Organization' that has no other members.
    """
    from apps.members.models import OrgMembership
    from apps.workspaces.models import Workspace

    stray = (
        OrgMembership.objects.filter(user=user)
        .exclude(organization=keep_org)
        .select_related("organization")
    )
    for membership in stray:
        org = membership.organization
        membership.delete()
        if org.name == "My Organization" and not org.memberships.exists():
            Workspace.objects.filter(organization=org).delete()
            org.delete()


@transaction.atomic
def provision_sso_user(*, email, name, app_id, app_slug, app_name, role):
    """Resolve (creating as needed) the user, org, workspace and memberships.

    Returns the Workspace the caller should redirect into.
    """
    from apps.members.models import OrgMembership, WorkspaceMembership
    from apps.sso.models import ExternalAppWorkspace
    from apps.workspaces.models import Workspace

    User = __import__("django.contrib.auth", fromlist=["get_user_model"]).get_user_model()

    org = get_or_create_shared_org()

    # 1. User (JIT). Creating a user fires post_save → a personal org we clean up.
    user, created = User.objects.get_or_create(
        email=email,
        defaults={"name": name or ""},
    )
    if created and name and not user.name:
        user.name = name
        user.save(update_fields=["name"])
    if created:
        _cleanup_auto_provisioned_org(user, keep_org=org)

    # 2. Org membership in the shared org.
    OrgMembership.objects.get_or_create(
        user=user,
        organization=org,
        defaults={"org_role": OrgMembership.OrgRole.MEMBER},
    )

    # 3. Workspace for this app (idempotent via the mapping table).
    link = ExternalAppWorkspace.objects.filter(external_app_id=str(app_id)).first()
    if link and not link.workspace.is_archived:
        workspace = link.workspace
        # Keep the display name fresh if it changed in admin.
        if app_name and workspace.name != app_name:
            workspace.name = app_name[:100]
            workspace.save(update_fields=["name"])
    else:
        workspace = Workspace.objects.create(
            organization=org,
            name=(app_name or app_slug or "Social Media")[:100],
            description="Social media workspace synced from Benerits admin.",
        )
        ExternalAppWorkspace.objects.update_or_create(
            external_app_id=str(app_id),
            defaults={
                "external_app_slug": app_slug or "",
                "organization": org,
                "workspace": workspace,
            },
        )

    # 4. Workspace membership with the mapped role.
    WorkspaceMembership.objects.get_or_create(
        user=user,
        workspace=workspace,
        defaults={"workspace_role": _map_workspace_role(role)},
    )

    # 5. Remember last workspace for clean dashboard redirects.
    if user.last_workspace_id != workspace.id:
        user.last_workspace_id = workspace.id
        user.save(update_fields=["last_workspace_id"])

    return user, workspace
