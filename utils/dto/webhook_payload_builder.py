def webhookCallbackState(data: dict):
    return {
        "id": data["monime_reference"],
        "reference": data["order_reference"],
        "amount": data["amount"],
        "currency_code": data["currency_code"],
        "status": data["status"],
    }
