def webhookCallbackState(data: dict):
    return {
        "reference": data["reference"],
        "amount": float(data["amount"]),
        "currency_code": data["currency_code"],
        "status": data["status"],
        "orderNumber": data["orderNumber"],
    }
