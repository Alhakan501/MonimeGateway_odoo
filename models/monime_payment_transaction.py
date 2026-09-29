from dataclasses import asdict
import logging
import uuid

from werkzeug import urls

from ..utils.dto.build_checkout_payload import buildCheckoutPayload

from ..utils.dto.build_line_items import buildLineItems
from ..utils.dto.build_payment_options import buildPaymentOptions

from ..utils.consts import CANCEL_URL, CURRENCIES, MONIME_URL, SUCCESSS_URL
from odoo import models

_logger = logging.getLogger(__name__)


class MonimePaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != "monime":
            return res

        order_names = ", ".join(self.sale_order_ids.mapped("name"))
        base_url = self.provider_id.get_base_url()
        payload = buildCheckoutPayload(
            name=self.env.company.name,
            line_items=buildLineItems(self),
            description=f"Payment for order {order_names}",
            cancel_url=urls.url_join(base_url, CANCEL_URL),
            success_url=urls.url_join(base_url, SUCCESSS_URL),
            callback_state=str(uuid.uuid4()),
            reference=self.reference,
            financial_account_id=self.provider_id.monime_financial_account,
            payment_options=buildPaymentOptions(self),
            metadata={"OrderId": order_names},
        )
        print(payload)

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
        redirect_url = result.get("redirectUrl")

        if not redirect_url:
            _logger.error(
                "Monime response missing redirectUrl: %(resp)s", {"resp": response}
            )
            self._set_error(_("Monime did not return a redirect URL."))
            raise ValidationError(_("Monime did not return a redirect URL."))

        return {"api_url": redirect_url}
