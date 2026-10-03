from dataclasses import asdict
import logging
import uuid

from werkzeug import urls

from odoo.exceptions import ValidationError


from odoo.http import url_encode
from odoo.orm.models import api
from ..utils.dto.build_checkout_payload import buildCheckoutPayload

from ..utils.dto.build_line_items import buildLineItems
from ..utils.dto.build_payment_options import buildPaymentOptions
from ..utils.dto.build_callback_state import buildCallbackState
from ..utils.consts import CANCEL_URL, CURRENCIES, MONIME_URL, SUCCESSS_URL
from odoo import fields, models

_logger = logging.getLogger(__name__)


class MonimePaymentTransaction(models.Model):
    _inherit = "payment.transaction"
    monime_checkout_id = fields.Char(string="Monime checkout id")

    @api.model
    def _search_by_reference(self, provider_code, payment_data):
        if provider_code != "monime":
            return super()._search_by_reference(provider_code, payment_data)

        reference = payment_data.get("reference")
        if not reference:
            _logger.warning(
                "Monime payment data missing reference: %(data)s",
                {"data": payment_data},
            )
            return self

        tx = self.search(
            [("reference", "=", reference), ("provider_code", "=", "monime")],
            limit=1,
        )
        if not tx:
            _logger.warning(
                "No Monime transaction found for reference %(ref)s", {"ref": reference}
            )
        return tx

    def _extract_reference(self, provider_code, payment_data):
        if provider_code != "monime":
            return super()._extract_reference(provider_code, payment_data)
        return payment_data.get("reference")

    def _extract_amount_data(self, payment_data):
        if self.provider_code != "monime":
            return super()._extract_amount_data(payment_data)
        if not payment_data or "amount" not in payment_data:
            return None
        amount_data = {
            "amount": payment_data.get("amount", 0),
            "currency_code": payment_data.get("currency_code"),
        }
        return amount_data

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != "monime":
            return res

        query = url_encode(buildCallbackState(self))
        order_names = ", ".join(self.sale_order_ids.mapped("name"))
        base_url = self.provider_id.get_base_url()

        payload = buildCheckoutPayload(
            name=self.env.company.name,
            line_items=buildLineItems(self),
            description=f"Payment for order {order_names}",
            cancel_url=urls.url_join(base_url, CANCEL_URL + "?" + query),
            success_url=urls.url_join(base_url, SUCCESSS_URL + "?" + query),
            financial_account_id=self.provider_id.monime_financial_account,
            payment_options=buildPaymentOptions(self),
            reference=self.reference,
            metadata={
                "amount": str(self.amount),
                "currency_code": self.currency_id.name,
            },
        )

        try:
            response = self._send_api_request("POST", "checkout-sessions", json=payload)

        except ValidationError as e:
            _logger.error(
                "Monime checkout session creation failed: %(err)s", {"err": str(e)}
            )
            self._set_error(str(e))
            raise

        if not response.get("success"):
            messages = response.get("messages") or [_("Unknown error from Monime.")]
            error_message = "; ".join(messages)
            _logger.error(
                "Monime returned success=false: %(msg)s", {"msg": error_message}
            )
            self._set_error(error_message)
            raise ValidationError(error_message)
        result = response.get("result") or {}

        print("\n")
        print(result, flush=True)
        self.monime_checkout_id = result.get("id")
        redirect_url = result.get("redirectUrl")

        if not redirect_url:
            _logger.error(
                "Monime response missing redirectUrl: %(resp)s", {"resp": response}
            )
            self._set_error(_("Monime did not return a redirect URL."))
            raise ValidationError(_("Monime did not return a redirect URL."))

        return {"api_url": redirect_url}

    def _apply_updates(self, payment_data):
        if self.provider_code != "monime":
            return super()._apply_updates(payment_data)

        if not payment_data:
            self._set_pending()
            return

        status = payment_data.get("status")
        provider_reference = payment_data.get("orderNumber")

        if provider_reference:
            self.provider_reference = provider_reference

        if status == "completed":
            self._set_done()

        elif status == "cancelled":
            self._set_canceled()
            self.sale_order_ids.action_cancel()

        else:
            _logger.warning(
                "Monime returned an unrecognized status %(status)s for tx %(ref)s.",
                {"status": status, "ref": self.reference},
            )
            self._set_canceled()
            self.sale_order_ids.action_cancel()
