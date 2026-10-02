# hooks.py
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    payment_method = env["account.payment.method"].search(
        [("code", "=", "monime")], limit=1
    )

    if not payment_method:
        env["account.payment.method"].create(
            {
                "name": "Monime",
                "code": "monime",
                "payment_type": "inbound",
            }
        )
        _logger.info("Monime: created account.payment.method.")
