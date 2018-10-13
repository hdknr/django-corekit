from dateutil.relativedelta import relativedelta


def relative_to(date, **params):
    # https://dateutil.readthedocs.io/en/stable/relativedelta.html
    # date: date or datetime
    return date + relativedelta(**params)