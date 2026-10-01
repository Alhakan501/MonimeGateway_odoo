import json


def buildCallbackState(tx, provider_reference):
    return {
        "id": provider_reference,
        "reference": tx.reference,
        "amount": tx.amount,
        "currency_code": tx.currency_id.name,
    }
