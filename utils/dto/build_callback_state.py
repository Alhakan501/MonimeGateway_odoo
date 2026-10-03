import json


def buildCallbackState(tx):
    return {
        "reference": tx.reference,
        "amount": tx.amount,
        "currency_code": tx.currency_id.name,
    }
