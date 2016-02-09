def is_num(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


# http://code.activestate.com/recipes/415233-getting-minmax-in-a-sequence-greaterless-than-some/
def min_ge(seq, val):
    """
    Same as min_gt() except items equal to val are accepted as well.

    :param seq:
    :param val:
    :return:

    Examples:
        min_ge([1, 3, 6, 7], 6)
        >>>6
        min_ge([2, 3, 4, 8], 8)
        >>>8
    """

    for v in seq:
        if v >= val:
            return v
    return None


def next_power_of_2(n):
    """
    Return next power of 2 greater than or equal to n
    """
    return 2**(n - 1).bit_length()


def is_power2(num):
    """
    states if a number is a power of two
    """
    return num != 0 and ((num & (num - 1)) == 0)
