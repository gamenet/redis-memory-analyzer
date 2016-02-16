from rma.helpers.formating import floored_percentage, pref_encoding, make_total_row
from rma.helpers.numbers import is_num, min_ge, next_power_of_2, is_power2


def progress_iterator(x, progress):
    for i in x:
        yield i
        progress.update()


__all__ = ['floored_percentage', 'pref_encoding', 'make_total_row', 'is_num', 'min_ge', 'next_power_of_2', 'is_power2',
           'progress_iterator']
