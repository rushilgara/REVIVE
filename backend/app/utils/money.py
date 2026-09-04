from decimal import Decimal, ROUND_HALF_UP
from typing import Union


def to_minor_units(amount_major: Union[int, str, Decimal]) -> int:
    """
    Converts a major currency value (e.g., 4999 or 4999.50) into integer minor units (paise).
    Guarantees no floating point arithmetic is performed.
    """
    if isinstance(amount_major, float):
        raise TypeError("Floats are prohibited in financial calculations. Pass int, str, or Decimal.")
    
    dec_amount = Decimal(str(amount_major))
    if dec_amount < 0:
        raise ValueError("Monetary amount cannot be negative.")
        
    minor = int((dec_amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return minor


def from_minor_units(amount_minor: int) -> Decimal:
    """
    Converts integer minor units (paise) into a precise Decimal major currency representation.
    """
    if not isinstance(amount_minor, int):
        raise TypeError(f"Minor units must be an integer, got {type(amount_minor).__name__}.")
    if amount_minor < 0:
        raise ValueError("Minor amount cannot be negative.")
        
    return (Decimal(amount_minor) / Decimal(100)).quantize(Decimal("0.01"))


def format_currency(amount_minor: int, currency: str = "INR") -> str:
    """
    Formats minor currency units into human-readable string.
    Example: 499900 -> '₹4,999' or '₹4,999.50'
    """
    major = from_minor_units(amount_minor)
    symbol = "₹" if currency == "INR" else f"{currency} "
    
    # Format with Indian grouping if INR
    if currency == "INR":
        # Format integer and decimal parts
        s, *d = f"{major:.2f}".partition(".")
        r = ",".join([s[x - 2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]]) if len(s) > 3 else s
        decimals = "".join(d)
        if decimals == ".00":
            return f"{symbol}{r}"
        return f"{symbol}{r}{decimals}"
    
    return f"{symbol}{major:,.2f}"


def calculate_erv(prob_percentage: int, amount_minor: int, intervention_cost_minor: int = 0) -> int:
    """
    Calculates Expected Recovery Value (ERV) strictly using integer arithmetic:
    ERV = (prob_percentage * amount_minor) // 100 - intervention_cost_minor
    Never returns negative value.
    """
    if prob_percentage < 0 or prob_percentage > 100:
        raise ValueError("Probability percentage must be between 0 and 100.")
    if amount_minor < 0:
        raise ValueError("Amount cannot be negative.")
        
    expected_gross = (prob_percentage * amount_minor) // 100
    erv = max(0, expected_gross - intervention_cost_minor)
    return erv
