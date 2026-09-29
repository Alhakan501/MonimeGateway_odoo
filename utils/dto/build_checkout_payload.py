def buildCheckoutPayload(
    name,
    line_items,
    description,
    cancel_url,
    success_url,
    callback_state,
    reference,
    financial_account_id,
    payment_options,
    metadata,
):
    payload = {
        "name": name,
        "lineItems": line_items,
        "description": description,
        "cancelUrl": cancel_url,
        "successUrl": success_url,
        "callbackState": callback_state,
        "reference": reference,
        "financialAccountId": financial_account_id,
        "paymentOptions": payment_options,
        "metadata": metadata,
    }
    return {k: v for k, v in payload.items() if v not in (None, False, "")}
