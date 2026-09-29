
# Monime Gateway for Odoo

Monime Payment Gateway integration for **Odoo 19**.

This module adds Monime as a payment provider in Odoo, allowing Odoo eCommerce customers to pay through Monime Checkout.

> **Status:** 🚧 Work in Progress
> The module is currently under active development.

## Overview

**Monime Gateway** connects Odoo's payment framework with the [Monime](https://monime.io) payment platform.

The module is designed to integrate with Odoo's native payment provider and transaction systems rather than implementing a separate checkout system.

The intended payment flow is:

```text
Odoo eCommerce
      │
      │ Customer selects Monime
      ▼
Odoo Payment Provider
      │
      │ Create payment request
      ▼
Monime Checkout
      │
      │ Customer completes payment
      ▼
Monime
      │
      │ Webhook
      ▼
Odoo Payment Transaction
      │
      ▼
Order Payment Confirmed
```

## Features

### Payment Provider

Adds **Monime** as an Odoo payment provider.

The provider is registered using Odoo's native:

```text
payment.provider
```

model.

### Monime Checkout

Payments are intended to be created through Monime Checkout, allowing customers to complete payment using the payment methods supported by their Monime account.

### Payment Transactions

The module integrates with Odoo's payment transaction framework so that payment attempts can be associated with Odoo orders.

### Webhooks

Monime webhooks are used to communicate payment status changes back to Odoo.

The webhook integration is responsible for updating the corresponding Odoo payment transaction after Monime processes the payment.

### Odoo eCommerce Integration

The provider is designed to work with Odoo's standard eCommerce payment flow.

This means the customer can select:

```text
Monime
```

during checkout instead of using a completely separate payment implementation.

---

# Requirements

## Odoo

Currently targeted at:

```text
Odoo 19
```

## Monime

You need a Monime account and the credentials required by the Monime API.

Depending on the implementation and environment, these may include:

* Monime API token
* Monime Space ID
* Webhook secret
* Financial account information

Never commit these credentials to Git.

---

# Installation

Clone the repository into your Odoo addons directory:

```bash
git clone https://github.com/Alhakan501/MonimeGateway.git
```

For example:

```text
odoo/
└── addons/
    └── MonimeGateway/
```

The module directory should contain:

```text
MonimeGateway/
├── __init__.py
├── __manifest__.py
├── controllers/
├── models/
├── views/
├── data/
└── static/
```

## Docker

If Odoo is running with Docker and your addons directory is mounted as:

```yaml
volumes:
  - ./addons:/mnt/extra-addons
```

place the module inside:

```text
./addons/MonimeGateway
```

Then restart Odoo:

```bash
docker compose restart odoo
```

Update the Apps list from Odoo or upgrade the module from the command line.

---

# Installing the Module

From the Odoo interface:

1. Open **Apps**.
2. Enable developer mode if necessary.
3. Click **Update Apps List**.
4. Search for:

```text
Monime Gateway
```

5. Click **Install**.

Alternatively, upgrade the module from the command line:

```bash
docker compose exec odoo odoo \
    -d odoo_test \
    -u MonimeGateway \
    --stop-after-init
```

Replace `odoo_test` with your Odoo database name.

---

# Configuration

After installation, the Monime provider should appear in Odoo's payment provider configuration.

The provider is represented internally by:

```text
payment.provider
```

with the provider code:

```text
monime
```

A typical provider configuration will contain credentials such as:

```text
Monime API Token
Monime Space ID
Webhook Secret
```

Credentials should be entered through Odoo's configuration interface and must not be hard-coded into Python source files.

---

# Payment Flow

The intended payment flow is:

### 1. Customer creates an order

The customer adds products to the Odoo shopping cart.

```text
Customer
   │
   ▼
Odoo Cart
```

### 2. Customer selects Monime

During checkout, the customer selects:

```text
Monime
```

### 3. Odoo creates a payment transaction

Odoo creates a payment transaction associated with the order.

```text
sale.order
     │
     ▼
payment.transaction
```

### 4. Odoo creates the Monime payment

The module sends the required payment information to Monime.

The request should contain the information required to identify the Odoo transaction and order.

For example:

```text
Reference
Amount
Currency
Customer information
Order information
Success URL
Cancel URL
```

### 5. Customer completes payment

The customer is redirected to Monime Checkout.

```text
Odoo
  │
  ▼
Monime Checkout
  │
  ▼
Customer Payment
```

### 6. Monime sends a webhook

After the payment state changes, Monime sends a webhook to Odoo.

```text
Monime
   │
   │ webhook
   ▼
Odoo Controller
```

### 7. Odoo updates the transaction

The webhook handler identifies the corresponding Odoo transaction and updates its state.

```text
payment.transaction
        │
        ▼
confirmed / pending / canceled / error
```

The Odoo order can then proceed according to its normal payment workflow.

---

# Webhooks

The module includes a webhook controller for receiving payment events from Monime.

The endpoint will be exposed by the Odoo HTTP controller.

The exact endpoint is defined by the module's controller implementation.

Example:

```text
https://your-odoo-domain.com/monime/webhook
```

Configure the corresponding URL in your Monime environment.

## Webhook Security

Webhook requests should be verified before changing an Odoo transaction.

The webhook handler should:

1. Receive the request.
2. Validate the webhook signature.
3. Identify the Monime payment.
4. Locate the corresponding Odoo transaction.
5. Verify the transaction amount/currency where applicable.
6. Update the Odoo transaction state.
7. Return an appropriate HTTP response.

Do not trust an incoming webhook simply because it contains a valid-looking transaction ID.

---

# Module Structure

The addon follows the standard Odoo module structure:

```text
MonimeGateway/
│
├── __init__.py
├── __manifest__.py
│
├── controllers/
│   ├── __init__.py
│   └── webhook.py
│
├── models/
│   ├── __init__.py
│   ├── payment_provider.py
│   └── payment_transaction.py
│
├── data/
│   └── payment_provider_data.xml
│
├── views/
│   └── payment_provider_views.xml
│
└── static/
    └── description/
        └── icon.svg
```

The exact structure may change as development continues.

---

# Main Components

## `__manifest__.py`

Defines the Odoo module metadata, dependencies, assets, and XML data files.

Example:

```python
{
    "name": "Monime Gateway",
    "version": "1.0.0",
    "category": "Accounting/Payment Providers",
    "depends": [
        "payment",
    ],
    "data": [
        "data/payment_provider_data.xml",
        "views/payment_provider_views.xml",
    ],
    "installable": True,
    "application": False,
}
```

## `models/payment_provider.py`

Extends Odoo's:

```python
payment.provider
```

This is where the Monime provider's behavior is implemented.

The provider identifies itself using:

```python
code = "monime"
```

and contains the provider-specific configuration and payment logic.

## `models/payment_transaction.py`

Extends:

```python
payment.transaction
```

This handles the Monime-specific transaction behavior.

Typical responsibilities include:

* Creating payment requests
* Processing payment responses
* Handling transaction references
* Processing notification data
* Updating transaction states

## `controllers/webhook.py`

Receives webhook notifications from Monime.

Its responsibility is to pass verified Monime events into Odoo's payment transaction system.

## `data/payment_provider_data.xml`

Creates the Monime payment provider record:

```xml
<record id="payment_provider_monime" model="payment.provider">
    <field name="name">Monime</field>
    <field name="code">monime</field>
</record>
```

## `views/payment_provider_views.xml`

Extends Odoo's payment provider interface with Monime-specific configuration.

---

# Development

Clone the repository:

```bash
git clone https://github.com/Alhakan501/MonimeGateway.git
cd MonimeGateway
```

If you're developing against an Odoo Docker installation, mount the repository into the Odoo addons directory.

For example:

```yaml
services:
  odoo:
    volumes:
      - ./addons:/mnt/extra-addons
```

Then place the addon at:

```text
addons/MonimeGateway
```

Restart Odoo:

```bash
docker compose restart odoo
```

---

# Updating the Module During Development

After changing Python code:

```bash
docker compose restart odoo
```

After changing XML, views, or module data:

```bash
docker compose exec odoo odoo \
    -d odoo_test \
    -u MonimeGateway \
    --stop-after-init
```

Then start Odoo again:

```bash
docker compose up -d
```

---

# Debugging

View the Odoo logs:

```bash
docker compose logs -f odoo
```

Or:

```bash
docker logs -f odoo-odoo-1
```

To update the module and immediately see installation errors:

```bash
docker compose exec odoo odoo \
    -d odoo_test \
    -u MonimeGateway \
    --stop-after-init
```

This is particularly useful for diagnosing:

* Python import errors
* XML parsing errors
* View inheritance errors
* Missing external IDs
* Model registration errors
* Payment provider errors
* Webhook errors

---

# Security

Payment credentials must never be committed to the repository.

Do not put credentials directly into:

```python
payment_provider.py
```

or:

```python
__manifest__.py
```

Do not commit:

```text
API tokens
Webhook secrets
Private keys
Production credentials
Database passwords
```

Webhook requests should also be authenticated and validated before modifying payment transactions.

---

# Current Development Status

The project is currently under development.

### Implemented / In Development

* [x] Odoo payment provider model
* [x] Monime provider registration
* [x] Odoo payment provider view
* [ ] Monime API integration
* [ ] Payment creation
* [ ] Payment redirect
* [ ] Transaction processing
* [ ] Webhook verification
* [ ] Webhook transaction updates
* [ ] Production configuration
* [ ] Automated tests
* [ ] Odoo eCommerce end-to-end testing

The checklist will be updated as functionality is completed.

---

# Roadmap

* [ ] Complete Monime API client integration
* [ ] Implement payment creation
* [ ] Implement checkout redirect
* [ ] Implement transaction state handling
* [ ] Implement webhook signature verification
* [ ] Implement webhook event processing
* [ ] Add configurable Monime credentials
* [ ] Add payment-method configuration
* [ ] Add comprehensive error handling
* [ ] Add automated tests
* [ ] Test Odoo eCommerce checkout
* [ ] Prepare production release

---

# Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch:

```bash
git checkout -b feature/your-feature
```

3. Make your changes.
4. Test the module against Odoo 19.
5. Commit your changes:

```bash
git commit -m "Add your feature"
```

6. Push the branch:

```bash
git push origin feature/your-feature
```

7. Open a pull request.

---

# License

See the repository license for licensing information.

---

# Links

**Repository:**
https://github.com/Alhakan501/MonimeGateway

**Monime:**
https://monime.io

**Odoo:**
https://www.odoo.com

---

## Disclaimer

This project is an independent Odoo integration for Monime. It is not an official Odoo module unless explicitly stated otherwise.
