from math import floor
from collections import Counter


def floored_percentage(val, digits):
    """
    Return string of floored value with given digits after period

    :param val:
    :param digits:
    :return:
    """
    val *= 10 ** (digits + 2)
    return '{1:.{0}f}%'.format(digits, floor(val) / 10 ** digits)


def pref_encoding(data, encoding_transform=None):
    """
    Return string with unique words in list with percentage of they frequency

    :param data:
    :param encoding_transform:
    :return str:
    """
    encoding_counted = Counter(data)
    total = sum(encoding_counted.values())
    sorted_encodings = sorted(encoding_counted.items(), key=lambda t: t[1], reverse=True)

    return ' / '.join(
            ["{:<1} [{:<4}]".format(encoding_transform(k) if encoding_transform else k,
                                    floored_percentage(v * 1.0 / total, 1)) for k, v in sorted_encodings])


def make_total_row(source, agg):
    """
    Execute agg column based function for source columns. For example if you need `total` in table data:

    Examples:
        src = [[1,1],[1,2],[1,3]]
        print(make_total_row(src, [sum, min]))
        >>> [3, 1]

    :param source:
    :param agg:
    :return:
    """
    return [agg[index](value) if callable(agg[index]) else agg[index] for index, value in enumerate(zip(*source))]
