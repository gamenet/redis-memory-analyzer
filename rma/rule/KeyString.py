from rma.Redis import *
from rma.helpers import *
from itertools import *

import statistics


class KeyString:
    def __init__(self, redis):
        """
        :param RmaRedis redis:
        :return:
        """
        self.redis = redis

    def analyze(self, keys):
        key_stat = {
            'headers': ['Match', "Count", "Useful", "Real", "Ratio", "Encoding", "Min", "Max", "Avg"],
            'data': []
        }

        for pattern, data in keys.items():
            used_bytes_iter, aligned_iter, encoding_iter = tee((StringEntry(value=x) for x in data), 3)

            total_elements = len(data)
            aligned = sum(obj.aligned for obj in aligned_iter)
            used_bytes_generator = (obj.useful_bytes for obj in used_bytes_iter)
            useful_iter, min_iter, max_iter, mean_iter = tee(used_bytes_generator, 4)

            prefered_encoding = pref_encoding(obj.encoding for obj in encoding_iter)
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
        key_stat['data'].append(total_row(key_stat['data'], ['Total:', sum, sum, sum, 0, '', 0, 0, 0]))

        return [
            "key stats",
            key_stat
        ]
