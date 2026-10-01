import base64
import hashlib
import hmac
import json
import time
import logging

_logger = logging.getLogger(__name__)


def validate_monime_webhook(raw_body: bytes, signature_header: str, secret: str):
    secret = (secret or "").strip()
    if not secret:
        _logger.error("Monime webhook secret not configured")
        return False, "Webhook secret not configured"

    if not signature_header:
        _logger.error("Monime webhook signature missing")
        return False, "Missing signature"

    timestamp = None
    signature = None
    for part in signature_header.split(","):
        part = part.strip()
        if part.startswith("t="):
            try:
                timestamp = int(part[2:])
            except ValueError:
                timestamp = None
        elif part.startswith("v1="):
            signature = part[3:].strip()

    if not timestamp or not signature:
        _logger.error("Monime webhook signature format invalid")
        return False, "Invalid signature format"

    now = int(time.time())
    if abs(now - timestamp) > 300:
        _logger.error(
            "Monime webhook signature timestamp expired: %(ts)s", {"ts": timestamp}
        )
        return False, "Timestamp expired"

    signed_payload = f"{timestamp}_".encode() + raw_body
    expected_signature = base64.b64encode(
        hmac.new(secret.encode(), signed_payload, hashlib.sha256).digest()
    ).decode()

    if not hmac.compare_digest(expected_signature, signature):
        _logger.error("Monime webhook signature mismatch")
        return False, "Invalid signature"

    try:
        data = json.loads(raw_body)
    except (ValueError, TypeError) as e:
        _logger.error("Monime webhook JSON invalid: %(err)s", {"err": str(e)})
        return False, "Invalid JSON"

    return True, data
