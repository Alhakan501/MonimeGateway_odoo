# from ..utils.dto.parse_response import parse_callback_state
import logging
from urllib.parse import quote

from ..utils.dto.webhook_payload_builder import webhookCallbackState

from ..utils.webhook_validation import validate_monime_webhook
from ..utils.consts import MONIME_WEBHOOK
from odoo import http


from odoo.http import request

_logger = logging.getLogger(__name__)


class MonimeController(http.Controller):
    @http.route(
        "/payment/monime/cancel",
        type="http",
        auth="public",
        csrf=False,
    )
    def monime_cancel(self, **data):

        data["status"] = "cancelled"
        data["amount"] = float(data["amount"])
        reference = data.get("reference")

        if not reference:
            _logger.warning(
                "Monime cancel callback missing reference: %(data)s", {"data": data}
            )
            return request.not_found()

        tx = (
            request.env["payment.transaction"]
            .sudo()
            .search([("reference", "=", reference)], limit=1)
        )
        if not tx:
            return request.not_found()
        if tx.state == "draft":
            _logger.info(
                "Transaction %(ref)s is still draft; canceling it.",
                {"ref": tx.reference},
            )

            tx._process("monime", data)

        elif tx.state == "cancel":
            _logger.info(
                "Transaction %(ref)s is already canceled; Create a new order",
                {"ref": tx.reference},
            )
            message = "Transaction %(ref)s is already canceled; Create a new order"
        else:
            _logger.info(
                "Transaction %(ref)s has already been processed; skipping cancellation.",
                {"ref": tx.reference, "state": tx.state},
            )
            message = (
                "Transaction %(ref)s has already been processed; skipping cancellation.",
            )

        return request.redirect(f"/payment/status?reference={reference}")

    @http.route(
        "/payment/monime/success",
        type="http",
        auth="public",
        csrf=False,
    )
    def monime_success(self, **data):

        reference = data.get("reference")

        if not reference:
            _logger.warning(
                "Monime success callback missing reference: %(data)s", {"data": data}
            )
            return request.not_found()

        tx = (
            request.env["payment.transaction"]
            .sudo()
            .search([("reference", "=", reference)], limit=1)
        )
        if not tx:
            return request.not_found()
        if tx.state == "draft":
            _logger.info(
                "Transaction %(ref)s is still draft; processing success.",
                {"ref": tx.reference},
            )

            data["status"] = "completed"
            data["amount"] = float(data["amount"])
            try:
                print("bout to... sart process")
                tx._process("monime", data)

                message = "Payment completed successfully."

            except Exception as e:
                _logger.exception(
                    "Could not process successful payment for tx %(ref)s",
                    {"ref": tx.reference},
                )

                message = "We could not complete the payment. Please try again."

        elif tx.state == "cancel":
            _logger.info(
                "Transaction %(ref)s is already canceled; ignoring success callback.",
                {"ref": tx.reference},
            )

            message = "This payment was already cancelled and cannot be completed."

        elif tx.state == "done":
            _logger.info(
                "Transaction %(ref)s is already completed.",
                {"ref": tx.reference},
            )

            message = "This payment has already been completed."

        else:
            _logger.info(
                "Transaction %(ref)s has already been processed; state=%(state)s.",
                {"ref": tx.reference, "state": tx.state},
            )

            message = "This payment has already been processed."

        return request.redirect(f"/payment/status?reference={reference}")

    @http.route(
        MONIME_WEBHOOK,
        auth="public",
        csrf=False,
        type="http",
        methods=["POST"],
    )
    def monime_webhook(self):
        raw_body = request.httprequest.get_data()
        signature_header = request.httprequest.headers.get("Monime-Signature", "")

        provider = (
            request.env["payment.provider"]
            .sudo()
            .search([("code", "=", "monime")], limit=1)
        )

        verified, result = validate_monime_webhook(
            raw_body, signature_header, provider.monime_webhook_token
        )
        if not verified:
            _logger.warning("Monime webhook rejected: %(reason)s", {"reason": result})
            return request.make_json_response(
                {"status": "error", "message": result}, status=401
            )

        event_data = result.get("data")
        status = event_data["status"]
        monime_reference = event_data["reference"]
        metadata = event_data["metadata"]
        order_reference = metadata["order_reference"]
        callback = {
            "monime_reference": monime_reference,
            "order_reference": order_reference,
            "amount": float(metadata["amount"]),
            "currency_code": metadata["currency_code"],
            "status": status,
        }
        data = webhookCallbackState(data=callback)
        print(order_reference)
        if not order_reference:
            _logger.warning(
                "Monime webhook missing order_reference: ", {"data": result}
            )
            return request.make_json_response({}, status=200)

        tx = (
            request.env["payment.transaction"]
            .sudo()
            .search([("reference", "=", order_reference)], limit=1)
        )
        if not tx:
            _logger.warning(
                "No transaction found for Monime webhook reference %(ref)s",
                {"ref": order_reference},
            )

            return

        if tx.state in ("done", "cancel", "error"):
            _logger.info(
                "Monime webhook for tx %(ref)s ignored — already in final state %(state)s.",
                {"ref": tx.reference, "state": tx.state},
            )
            return request.make_json_response({}, status=200)

        try:
            tx._process("monime", data)

        except Exception:
            _logger.exception(
                "Error processing Monime webhook for tx %(ref)s", {"ref": tx.reference}
            )

        return request.make_json_response({}, status=200)
