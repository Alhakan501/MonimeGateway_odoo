def _split_providers(value):
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def buildPaymentOptions(options):
    provider = options.provider_id
    return {
        "card": {
            "disable": provider.monime_card_disable,
        },
        "bank": {
            "disable": provider.monime_bank_disable,
            "enabledProviders": [],
            "disabledProviders": _split_providers(
                provider.monime_bank_disable_providers
            ),
        },
        "momo": {
            "disable": provider.monime_momo_disable,
            "enabledProviders": [],
            "disabledProviders": _split_providers(
                provider.monime_momo_disable_providers
            ),
        },
        "wallet": {
            "disable": provider.monime_wallet_disable,
            "enabledProviders": [],
            "disabledProviders": _split_providers(
                provider.monime_wallet_disable_providers
            ),
        },
    }
