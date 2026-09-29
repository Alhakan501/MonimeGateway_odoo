def buildPaymentOptions(options):
    provider = options.provider_id
    return {
        "card": {
            "disable": provider.monime_card_disable,
        },
        "bank": {
            "disable": provider.monime_bank_disable,
            "enabledProviders": [],
            "disabledProviders": [provider.monime_bank_disable_providers]
            if provider.monime_bank_disable
            else [],
        },
        "momo": {
            "disable": provider.monime_momo_disable,
            "enabledProviders": [],
            "disabledProviders": [provider.monime_momo_disable_providers]
            if provider.monime_momo_disable
            else [],
        },
        "wallet": {
            "disable": provider.monime_wallet_disable,
            "enabledProviders": [],
            "disabledProviders": [provider.monime_wallet_disable_providers]
            if provider.monime_wallet_disable
            else [],
        },
    }
