"""Public Terms of Service and Privacy Policy pages.

These are required by platform OAuth app reviews (e.g. TikTok) and must be
reachable without authentication. Rendered standalone so they don't pull in
the authenticated dashboard chrome.
"""

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.cache import cache_control

# Keep the last-updated date in one place so both pages stay in sync.
LAST_UPDATED = "16 June 2026"
COMPANY = "Benerits"
APP_NAME = "Benerits Social"


def _context():
    return {
        "last_updated": LAST_UPDATED,
        "company": COMPANY,
        "app_name": APP_NAME,
        "app_url": getattr(settings, "APP_URL", "https://studio.benerits.com"),
        "contact_email": "legal@benerits.com",
    }


@cache_control(public=True, max_age=3600)
def terms(request):
    return render(request, "legal/terms.html", _context())


@cache_control(public=True, max_age=3600)
def privacy(request):
    return render(request, "legal/privacy.html", _context())
