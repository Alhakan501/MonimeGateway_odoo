import uuid
from werkzeug import urls
from ..utils.consts import CURRENCIES, MONIME_URL, MONIME_WEBHOOK
from odoo import _, fields, models


class MonimePaymentProvider(models.Model):
    _inherit = "payment.provider"
    code = fields.Selection(
        selection_add=[("monime", "Monime")], ondelete={"monime": "set default"}
    )
    monime_space_id = fields.Char(
        string="Monime Space Id",
        required_if_provider="monime",
        help="Enter your Monime Space Id",
    )
    monime_token = fields.Char(
        string="Monime Token",
        required_if_provider="monime",
        help="Enter your Monime Token",
    )
    monime_webhook_token = fields.Char(
        string="Monime Webhook secret",
        required=False,
        default=None,
        help="Enter your generated webhook token",
    )
    monime_webhook_url = fields.Char(
        string="Webhook URL",
        compute="_compute_monime_webhook_url",
        help="Paste this URL into your Monime dashboard as the webhook endpoint.",
    )

    # -------------------------
    # ---- Configuration ----
    # ------------------------
    #
    monime_financial_account = fields.Char(
        string="Financial Account ID",
        help="Your Monime Financial Account ID. This determines which account "
        "receives the payments. Leave blank to use your default account.",
    )

    # Card
    monime_card_disable = fields.Boolean(
        string="Disable Card Payments",
        help="Disable card payments entirely.",
    )

    # Mobile Money
    monime_momo_disable = fields.Boolean(
        string="Disable Mobile Money",
        help="Disable mobile money payments entirely.",
    )
    monime_momo_disable_providers = fields.Char(
        string="Mobile Money - Disabled Providers",
        help="Comma-separated list of Mobile Money provider IDs to exclude "
        "for this session.",
    )

    # Bank transfer
    monime_bank_disable = fields.Boolean(
        string="Disable Bank Transfers",
        help="Disable bank transfer payments entirely.",
    )
    monime_bank_disable_providers = fields.Char(
        string="Bank - Disabled Providers",
        help="Comma-separated list of bank provider IDs to disable.",
    )

    # Digital wallets
    monime_wallet_disable = fields.Boolean(
        string="Disable Digital Wallets",
        help="Disable digital wallet payments entirely.",
    )
    monime_wallet_disable_providers = fields.Char(
        string="Wallet - Disabled Providers",
        help="Comma-separated list of wallet provider IDs to disable.",
    )

    # --------------------------------methods-------------------------------
    # ----------------------------------------------------------------------

    def _compute_monime_webhook_url(self):
        for provider in self:
            base_url = provider.get_base_url().rstrip("/")
            provider.monime_webhook_url = urls.url_join(base_url, MONIME_WEBHOOK)

    def _build_request_headers(self, method, endpoint, payload, **kwargs):
        self.ensure_one()
        if self.code != "monime":
            return super()._build_request_headers(method, endpoint, payload, **kwargs)
        return {
            "Authorization": f"Bearer {self.monime_token}",
            "Content-Type": "application/json",
            "Monime-Space-Id": self.monime_space_id,
            "Idempotency-Key": str(uuid.uuid4()),
        }

    def _build_request_url(self, endpoint, **kwargs):
        if self.code != "monime":
            return super()._build_request_url(endpoint, **kwargs)
        return f"{MONIME_URL}/{endpoint.lstrip('/')}"

    def _get_supported_currencies(self):
        supported_currencies = super()._get_supported_currencies()
        if self.code == "monime":
            return self.env["res.currency"].search([("name", "in", CURRENCIES)])
        return supported_currencies

    def _is_tokenization_supported(self):
        if self.code == "monime":
            return False
        return super()._is_tokenization_supported()

    def _get_default_payment_method_codes(self):
        self.ensure_one()
        if self.code != "monime":
            return super()._get_default_payment_method_codes()
        return {"monime"}

    def _should_build_inline_form(self, is_validation=False):
        if self.code != "monime":
            return super()._should_build_inline_form(is_validation)
        return False

    def _get_redirect_form_view(self, is_validation=False):
        if self.code == "monime":
            return self.env.ref("MonimeGateway.redirect_form")
        return super()._get_redirect_form_view(is_validation)
