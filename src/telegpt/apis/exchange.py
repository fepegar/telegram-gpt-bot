from functools import cache

from currency_converter import CurrencyConverter


@cache
def get_rate(from_currency: str, to_currency: str) -> float:
    converter = CurrencyConverter()
    rate = converter.convert(1, from_currency, to_currency)
    assert isinstance(rate, float)
    return rate


def usd_to_gbp(usd: float) -> float:
    rate = get_rate("USD", "GBP")
    gbp = usd * rate
    return gbp
