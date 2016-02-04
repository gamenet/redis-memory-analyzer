from math import floor
from collections import Counter


def floored_percentage(val, digits):
    val *= 10 ** (digits + 2)
    return '{1:.{0}f}%'.format(digits, floor(val) / 10 ** digits)


def pref_encoding(data):
    encoding_counted = Counter(data)
    prefered_encoding = max(encoding_counted, key=encoding_counted.get)
    total = sum(encoding_counted.values())
    return "{:<7} [{:<6}]".format(prefered_encoding, floored_percentage(encoding_counted[prefered_encoding] * 1.0 / total, 1))


def total_row(source, agg):
    return [agg[index](value) if callable(agg[index]) else agg[index] for index, value in enumerate(zip(*source))]