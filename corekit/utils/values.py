from decimal import Decimal, ROUND_CEILING


def _V(value):
    return isinstance(value, Decimal) and value or Decimal(str(value))


def ceil(value, base=Decimal('0')):
    return _V(value).quantize(base, rounding=ROUND_CEILING)


def taxed(value, rate=Decimal('0.08'), total=True):
    rate = total and (Decimal(1.0) + rate) or rate
    value = _V(value) * rate
    return ceil(value)
