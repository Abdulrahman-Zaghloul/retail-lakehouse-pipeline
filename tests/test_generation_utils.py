from decimal import Decimal

from src.generation.generate_retail_data import money


def test_money_rounds_to_two_decimal_places():
    assert money(Decimal("10.235")) == Decimal("10.24")
    assert money(Decimal("10.234")) == Decimal("10.23")


def test_money_returns_decimal():
    result = money(12.5)

    assert isinstance(result, Decimal)
    assert result == Decimal("12.50")
