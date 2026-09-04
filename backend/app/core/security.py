import hmac
import hashlib
from typing import Union


def verify_razorpay_signature(raw_body: Union[bytes, str], signature: str, secret: str) -> bool:
    """
    Verifies the Razorpay webhook signature using HMAC-SHA256.
    The raw unparsed request body bytes must be used.
    """
    if not signature or not secret:
        return False
    
    if isinstance(raw_body, str):
        body_bytes = raw_body.encode("utf-8")
    else:
        body_bytes = raw_body

    expected_signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=body_bytes,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)
