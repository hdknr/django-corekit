from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR


def _V(value):
    return isinstance(value, Decimal) and value or Decimal(str(value))


def ceil(value, base=Decimal('0')):
    value, base = _V(value), _V(base)
    return value.quantize(base, rounding=ROUND_CEILING)


def floor(value, base=Decimal('0')):
    value, base = _V(value), _V(base)
    return value.quantize(base, rounding=ROUND_FLOOR)


def taxed(value, rate=Decimal('0.10'), total=True):
    rate = total and (Decimal(1.0) + rate) or rate
    value = _V(value) * rate
    return ceil(value)
