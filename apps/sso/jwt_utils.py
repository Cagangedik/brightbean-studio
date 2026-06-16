"""Verify the HS256 SSO tickets minted by the Benerits admin panel.

The admin signs a compact JWT (see lib/sso/brightbean.ts there) with a shared
secret. We verify signature + claims here without a third-party JWT library,
mirroring the stdlib approach used elsewhere in the codebase.

A valid ticket is single-use: its ``jti`` is recorded in the cache for the
ticket's lifetime so replays within the window are rejected.
"""

import base64
import hashlib
import hmac
import json
import time

from django.conf import settings
from django.core.cache import cache

ISSUER = "benerits-admin"
AUDIENCE = "brightbean-studio"

# Reject tickets older than this even if exp somehow allows it (defense in
# depth against a misconfigured/oversized exp on the signer side).
MAX_TICKET_AGE_SECONDS = 300


class TicketError(Exception):
    """Raised when a ticket is missing, malformed, expired, or replayed."""


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def _get_secret() -> str:
    secret = getattr(settings, "BRIGHTBEAN_SSO_SECRET", "") or ""
    if len(secret) < 32:
        raise TicketError("SSO is not configured (BRIGHTBEAN_SSO_SECRET missing or too short).")
    return secret


def verify_ticket(token: str) -> dict:
    """Validate a ticket and return its payload claims, or raise TicketError."""
    if not token or token.count(".") != 2:
        raise TicketError("Malformed ticket.")

    secret = _get_secret()
    header_b64, payload_b64, signature_b64 = token.split(".")
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")

    # 1. Signature (constant-time compare).
    expected = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    try:
        provided = _b64url_decode(signature_b64)
    except Exception as exc:  # noqa: BLE001
        raise TicketError("Bad signature encoding.") from exc
    if not hmac.compare_digest(expected, provided):
        raise TicketError("Invalid signature.")

    # 2. Header alg.
    try:
        header = json.loads(_b64url_decode(header_b64))
    except Exception as exc:  # noqa: BLE001
        raise TicketError("Bad header.") from exc
    if header.get("alg") != "HS256":
        raise TicketError("Unexpected signing algorithm.")

    # 3. Payload + claims.
    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except Exception as exc:  # noqa: BLE001
        raise TicketError("Bad payload.") from exc

    if payload.get("iss") != ISSUER:
        raise TicketError("Wrong issuer.")
    if payload.get("aud") != AUDIENCE:
        raise TicketError("Wrong audience.")

    now = int(time.time())
    exp = payload.get("exp")
    iat = payload.get("iat")
    if not isinstance(exp, int) or now >= exp:
        raise TicketError("Ticket expired.")
    if not isinstance(iat, int) or now - iat > MAX_TICKET_AGE_SECONDS:
        raise TicketError("Ticket too old.")
    # Small clock-skew tolerance for iat in the future.
    if iat - now > 60:
        raise TicketError("Ticket issued in the future.")

    email = payload.get("email")
    if not email or "@" not in email:
        raise TicketError("Ticket missing a valid email.")
    if not payload.get("app_id"):
        raise TicketError("Ticket missing app_id.")

    # 4. Single-use: claim the jti for the remaining lifetime of the ticket.
    jti = payload.get("jti")
    if not jti:
        raise TicketError("Ticket missing jti.")
    cache_key = f"sso:jti:{jti}"
    ttl = max(1, exp - now)
    # cache.add returns False if the key already exists → replay.
    if not cache.add(cache_key, "1", timeout=ttl):
        raise TicketError("Ticket already used.")

    return payload
