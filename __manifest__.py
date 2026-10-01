{
    "name": "Monime Gateway",
    "version": "1.0.0",
    "summary": "Monime Gateway payment addon",
    "category": "Accounting/Payment Providers",
    "data": [
        "data/payment_method_data.xml",
        "data/payment_provider_data.xml",
        "views/monime_redirection.xml",
        "views/monime_settings_views.xml",
    ],
    "description": "Monime Official payment gateway addon for odoo ",
    "assets": {
        "web.assets_backend": [
            "MonimeGateway/static/src/style.css",
        ],
    },
    "author": "Monime",
    "license": "LGPL-3",
    "depends": ["payment"],
    "installable": True,
    "application": True,
}

# _build_request_url
