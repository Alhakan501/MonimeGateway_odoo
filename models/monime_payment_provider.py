from odoo import _, fields, models
from odoo.orm.fields_misc import copy


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
