import uuid
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger
from app.core.security import verify_razorpay_signature
from app.core.exceptions import RazorpayIntegrationException


class RazorpayService:
    """
    Official Razorpay Test Mode & Simulation Service.
    Supports official Razorpay APIs:
    - Payment Links (create, fetch, cancel)
    - Payments (fetch)
    - Subscriptions (fetch)
    - Webhook signature verification (HMAC SHA-256)
    
    Seamlessly switches between 'simulation' and 'real_test' mode.
    """

    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        self.mode = settings.INTEGRATION_MODE
        self.base_url = "https://api.razorpay.com/v1"

    async def create_payment_link(
        self,
        amount_minor: int,
        currency: str,
        description: str,
        customer_name: str,
        customer_email: str,
        customer_phone: Optional[str] = None,
        notes: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Creates a Razorpay payment link."""
        if self.mode == "real_test":
            payload = {
                "amount": amount_minor,
                "currency": currency,
                "accept_partial": False,
                "description": description,
                "customer": {
                    "name": customer_name,
                    "email": customer_email,
                    "contact": customer_phone or "+919876543210",
                },
                "notify": {
                    "sms": True,
                    "email": True
                },
                "reminder_enable": True,
                "notes": notes or {},
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.post(
                        f"{self.base_url}/payment_links",
                        auth=(self.key_id, self.key_secret),
                        json=payload
                    )
                    if res.status_code not in (200, 201):
                        raise RazorpayIntegrationException(
                            f"Razorpay API error: {res.status_code} - {res.text}",
                            status_code=res.status_code
                        )
                    return res.json()
            except httpx.RequestError as e:
                logger.error(f"Razorpay connection error: {e}")
                raise RazorpayIntegrationException(f"Failed to connect to Razorpay: {e}")
        else:
            # Deterministic simulation mode
            link_id = f"plink_{uuid.uuid4().hex[:14]}"
            return {
                "id": link_id,
                "amount": amount_minor,
                "currency": currency,
                "status": "created",
                "short_url": f"https://rzp.io/i/sim_{link_id[6:]}",
                "description": description,
                "customer": {
                    "name": customer_name,
                    "email": customer_email,
                    "contact": customer_phone or "+919876543210"
                },
                "mode": "simulation",
                "notes": notes or {}
            }

    async def fetch_payment(self, payment_id: str) -> Dict[str, Any]:
        """Fetches payment details from Razorpay."""
        if self.mode == "real_test":
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.get(
                        f"{self.base_url}/payments/{payment_id}",
                        auth=(self.key_id, self.key_secret)
                    )
                    if res.status_code != 200:
                        raise RazorpayIntegrationException(f"Payment fetch failed: {res.text}")
                    return res.json()
            except httpx.RequestError as e:
                raise RazorpayIntegrationException(f"Connection failed: {e}")
        else:
            return {
                "id": payment_id,
                "entity": "payment",
                "amount": 499900,
                "currency": "INR",
                "status": "captured",
                "method": "upi",
                "mode": "simulation"
            }

    async def fetch_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Fetches subscription details from Razorpay."""
        if self.mode == "real_test":
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.get(
                        f"{self.base_url}/subscriptions/{subscription_id}",
                        auth=(self.key_id, self.key_secret)
                    )
                    if res.status_code != 200:
                        raise RazorpayIntegrationException(f"Subscription fetch failed: {res.text}")
                    return res.json()
            except httpx.RequestError as e:
                raise RazorpayIntegrationException(f"Connection failed: {e}")
        else:
            return {
                "id": subscription_id,
                "status": "active",
                "mode": "simulation"
            }

    def verify_webhook_signature(self, raw_body: bytes, signature: str) -> bool:
        """Verifies HMAC SHA-256 signature of incoming Razorpay webhook."""
        if self.mode == "simulation" and signature == "simulated_valid_signature":
            return True
        return verify_razorpay_signature(raw_body, signature, self.webhook_secret)


razorpay_service = RazorpayService()
