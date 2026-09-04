# REVIVE — Razorpay API & Webhook Integration Guide

## 1. Overview & Dual Integration Modes

REVIVE is built from the ground up to integrate natively with **Razorpay's Payment Links and Webhook infrastructure**.

To allow seamless demonstration without requiring live API keys while supporting instant production deployment, REVIVE supports two runtime modes configured via `.env`:

```env
# Mode 1: Deterministic Test Simulation (Default for Judges / Offline Demo)
INTEGRATION_MODE=simulation

# Mode 2: Live Razorpay Test Mode / Production (With Real Credentials)
INTEGRATION_MODE=test
RAZORPAY_KEY_ID=rzp_test_YourKeyIdHere
RAZORPAY_KEY_SECRET=YourKeySecretHere
RAZORPAY_WEBHOOK_SECRET=YourWebhookSecretHere
```

---

## 2. Payment Link Generation API

When REVIVE decides on an interactive payment link intervention (`send_payment_link`), `RazorpayService.create_payment_link()` invokes Razorpay's Standard Payment Links API:

### Request Payload (`POST https://api.razorpay.com/v1/payment_links/`)
```json
{
  "amount": 499900,
  "currency": "INR",
  "accept_partial": false,
  "description": "Payment recovery for Order #TXN-4999",
  "customer": {
    "name": "Aarav Sharma",
    "email": "aarav.sharma@example.com",
    "contact": "+919876543210"
  },
  "notify": {
    "sms": true,
    "email": true,
    "whatsapp": true
  },
  "reminder_enable": true,
  "notes": {
    "recovery_case_id": "case_01J6...",
    "source": "REVIVE_ORCHESTRATION"
  },
  "callback_url": "http://localhost:5173/recovery/case_01J6...",
  "callback_method": "get"
}
```

### Response Model
The response returns a unique payment link URL (`https://rzp.io/i/abcdef123`) and a `plink_id` (e.g., `plink_01J6...`). REVIVE records this in the `interventions` table with state `EXECUTED`.

---

## 3. Webhook Authentication & Signature Verification

In accordance with Razorpay's security specifications, all incoming webhooks are validated using **HMAC-SHA256**:

```python
# Signature Verification in backend/app/services/razorpay_service.py
import hmac
import hashlib

def verify_webhook_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    expected_signature = hmac.new(
        key=secret.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)
```

If the signature fails verification, REVIVE rejects the request with `HTTP 400 Bad Request` and writes a security alert to the immutable audit log.

---

## 4. Webhook Event Handling & State Machine Synchronization

| Razorpay Event | REVIVE Handler Action | Resulting Case State |
| :--- | :--- | :---: |
| `payment.captured` | Verifies amount & payment ID $\to$ records financial recovery in ledger | `RECOVERED` |
| `payment.failed` | Records retry attempt $\to$ checks max retry ceiling | `EXECUTING` or `FAILED` |
| `payment_link.paid` | Matches payment link ID $\to$ marks intervention resolved | `RECOVERED` |
| `payment_link.expired` | Closes active link $\to$ schedules alternative channel or fallback | `DIAGNOSING` or `FAILED` |
| `payment_link.cancelled`| Flags customer-initiated cancellation | `STOPPED` |

---

## 5. Outcome Verification Invariant

**Crucial Architecture Requirement**:
REVIVE never marks a recovery case as `RECOVERED` merely because an action was dispatched or a link was generated.

A case is marked `RECOVERED` **if and only if**:
1. An authentic `payment.captured` or `payment_link.paid` webhook event is validated, OR
2. The `OutcomeEngine` directly queries the Razorpay API (`GET /v1/payments/{id}`) and validates that `status == "captured"`.
