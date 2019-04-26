from decimal import Decimal, ROUND_CEILING


def ceil(value, base=Decimal('0')):
    value = isinstance(value, Decimal) and value or Decimal(str(value))
    return value.quantize(base, rounding=ROUND_CEILING)
