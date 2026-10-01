def buildLineItems(tx):
    base_url = tx.get_base_url().rstrip("/")
    line_items = []
    for order in tx.sale_order_ids:
        for line in order.order_line:
            value = int(line.price_total * 100)

            if line.is_delivery or value == 0:
                continue
            line_items.append(
                {
                    "name": line.product_id.name,
                    "price": {
                        "currency": tx.currency_id.name,
                        "value": int(line.price_unit * 100),
                    },
                    "quantity": int(line.product_uom_qty),
                    "images": (
                        [
                            f"{base_url}/web/image/product.product/{line.product_id.id}/image_128"
                        ]
                        if line.product_id.image_128
                        else []
                    ),
                }
            )
    return line_items
