import pytest
from decimal import Decimal
from app.utils.money import to_minor_units, from_minor_units, format_currency, calculate_erv


def test_money_minor_units_conversion():
    # ₹1 -> 100 paise
    assert to_minor_units(1) == 100
    assert to_minor_units("1") == 100
    assert to_minor_units(Decimal("1.00")) == 100
    assert from_minor_units(100) == Decimal("1.00")

    # ₹999 -> 99900 paise
    assert to_minor_units(999) == 99900
    assert from_minor_units(99900) == Decimal("999.00")

    # ₹4,999 -> 499900 paise
    assert to_minor_units(4999) == 499900
    assert from_minor_units(499900) == Decimal("4999.00")

    # ₹50,000 -> 5000000 paise
    assert to_minor_units(50000) == 5000000
    assert from_minor_units(5000000) == Decimal("50000.00")

    # ₹87,000 -> 8700000 paise
    assert to_minor_units(87000) == 8700000
    assert from_minor_units(8700000) == Decimal("87000.00")

    # Large amount: ₹10,00,000 (10 Lakhs) -> 100000000 paise
    assert to_minor_units(1000000) == 100000000
    assert from_minor_units(100000000) == Decimal("1000000.00")


def test_floats_are_strictly_prohibited():
    with pytest.raises(TypeError, match="Floats are prohibited"):
        to_minor_units(4999.50)


def test_negative_amounts_prohibited():
    with pytest.raises(ValueError, match="cannot be negative"):
        to_minor_units(-100)
    with pytest.raises(ValueError, match="cannot be negative"):
        from_minor_units(-500)


def test_currency_formatting():
    assert format_currency(499900, "INR") == "₹4,999"
    assert format_currency(5000000, "INR") == "₹50,000"
    assert format_currency(8700000, "INR") == "₹87,000"
    assert format_currency(100, "INR") == "₹1"


def test_erv_calculation():
    # 80% recoverability on ₹4,999 (499900 paise) with ₹2 cost (200 paise)
    # Expected gross = (80 * 499900) // 100 = 399920 paise
    # Net ERV = 399920 - 200 = 399720 paise
    erv = calculate_erv(prob_percentage=80, amount_minor=499900, intervention_cost_minor=200)
    assert erv == 399720

    # 0% probability yields 0
    assert calculate_erv(prob_percentage=0, amount_minor=499900, intervention_cost_minor=200) == 0
