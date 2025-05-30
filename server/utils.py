from datetime import datetime


def datetime_as_string(d: datetime):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")