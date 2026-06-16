import uuid

from django.db import models


class ExternalAppWorkspace(models.Model):
    """Maps an external admin "app" to its dedicated Brightbean workspace.

    The Benerits admin panel manages many apps; each one gets its own
    isolated Brightbean workspace (all under a single shared organization).
    Keying on the external app id (a UUID from the admin DB) guarantees the
    same app always resolves to the same workspace, even if its display name
    changes on either side.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The external app's identifier (admin panel `app.id`). Indexed + unique.
    external_app_id = models.CharField(max_length=255, unique=True)
    external_app_slug = models.CharField(max_length=255, blank=True, default="")

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="external_app_workspaces",
    )
    workspace = models.OneToOneField(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="external_app_link",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "External app ↔ workspace link"

    def __str__(self):
        return f"{self.external_app_slug or self.external_app_id} → {self.workspace_id}"
