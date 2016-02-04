import statistics
from rma.Redis import *
from rma.helpers import *


class ValueString:
    def __init__(self, redis):
        self.redis = redis

    def analyze(self, keys):
        key_stat = {
            'headers': ['Match', "Count", "Useful", "Free", "Real", "Ratio", "Encoding", "Min", "Max", "Avg"],
            'data': []
        }

        for pattern, data in keys.items():
            used_bytes = []
            free_bytes = []
            aligned_bytes = []
            encodings = []

            for x in data:
                with RealStringEntry(key_name=x, redis=self.redis) as stat:
                    used_bytes.append(stat.useful_bytes)
                    free_bytes.append(stat.free_bytes)
                    aligned_bytes.append(stat.aligned)
                    encodings.append(stat.encoding)

            total_elements = len(used_bytes)
            used_user = sum(used_bytes)
            free_user = sum(free_bytes)
            aligned = sum(aligned_bytes)
            prefered_encoding = pref_encoding(encodings)

            min_bytes = min(used_bytes)
            mean = statistics.mean(used_bytes) if total_elements > 1 else min_bytes;

            stat_entry = [
                pattern, total_elements, used_user, free_user, aligned, aligned / (used_user if used_user > 0 else 1), prefered_encoding,
                min_bytes, max(used_bytes), mean,
            ]
            key_stat['data'].append(stat_entry)

        key_stat['data'].sort(key=lambda x: x[1], reverse=True)
        key_stat['data'].append(total_row(key_stat['data'], [ 'Total:', sum,sum,0,sum,0,'',0,0,0]))

        return [
            "String value stat",
            key_stat
        ]