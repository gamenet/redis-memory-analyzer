import statistics
from tqdm import tqdm
from itertools import tee
from rma.redis import *
from rma.helpers import pref_encoding, make_total_row, progress_iterator


class StringEntry(object):
    def __init__(self, value=""):
        self.encoding = get_string_encoding(value)
        self.useful_bytes = len(value)
        self.free_bytes = 0
        self.aligned = size_of_aligned_string(value, encoding=self.encoding)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class KeyString(object):
    def __init__(self, redis):
        """
        :param RmaRedis redis:
        :return:
        """
        self.redis = redis

    def analyze(self, keys, total=0):
        """

        :param keys:
        :param progress:
        :return:
        """
        key_stat = {
            'headers': ['Match', "Count", "Useful", "Real", "Ratio", "Encoding", "Min", "Max", "Avg"],
            'data': []
        }

        progress = tqdm(total=total,
                        mininterval=1,
                        desc="Processing keys",
                        leave=False)

        for pattern, data in keys.items():
            used_bytes_iter, aligned_iter, encoding_iter = tee(
                    progress_iterator((StringEntry(value=x["name"]) for x in data), progress), 3)

            total_elements = len(data)
            if total_elements == 0:
                continue

            aligned = sum(obj.aligned for obj in aligned_iter)
            used_bytes_generator = (obj.useful_bytes for obj in used_bytes_iter)
            useful_iter, min_iter, max_iter, mean_iter = tee(used_bytes_generator, 4)

            prefered_encoding = pref_encoding((obj.encoding for obj in encoding_iter), redis_encoding_id_to_str)
            min_value = min(min_iter)
            if total_elements < 2:
                avg = min_value
            else:
                avg = statistics.mean(mean_iter)

            used_user = sum(useful_iter)

            stat_entry = [
                pattern, total_elements, used_user, aligned, aligned / used_user, prefered_encoding,
                min_value, max(max_iter), avg,
            ]
            key_stat['data'].append(stat_entry)

        key_stat['data'].sort(key=lambda x: x[1], reverse=True)
        key_stat['data'].append(make_total_row(key_stat['data'], ['Total:', sum, sum, sum, 0, '', 0, 0, 0]))

        progress.close()

        return key_stat
