from itertools import tee
from rma.redis import *
from rma.helpers import pref_encoding, make_total_row

import statistics


class SetStatEntry(object):
    def __init__(self, info, redis):
        """
        :param key_name:
        :param RmaRedis redis:
        :return:
        """

        key_name = info["name"]
        self.values = [v for v in redis.sscan_iter(key_name, '*', 1000)]
        self.encoding = info["encoding"]
        self.count = len(self.values)

        if self.encoding == REDIS_ENCODING_ID_HASHTABLE:
            self.system = dict_overhead(self.count)
            self.valueUsedBytes = sum((len(x) for x in self.values))
            self.valueAlignedBytes = sum(map(size_of_aligned_string, self.values))
            self.total = self.valueAlignedBytes + self.system
        elif self.encoding == REDIS_ENCODING_ID_INTSET:
            self.system = intset_overhead(self.count)
            # In case if intset valueAlignedBytes already contains system overhead
            self.valueAlignedBytes = sum(map(size_of_ziplist_aligned_string, self.values))
            self.valueUsedBytes = self.valueAlignedBytes
            self.total = self.valueAlignedBytes
        else:
            raise Exception('Panic', 'Unknown encoding %s in %s' % (self.encoding, key_name))


class SetAggregator(object):
    def __init__(self, all_obj, total):
        self.total_elements = total

        g00, g0, g3, v1, v2, v3 = tee(all_obj, 6)

        self.encoding = pref_encoding([obj.encoding for obj in g00], redis_encoding_id_to_str)
        self.system = sum(obj.system for obj in g0)
        if total > 1:
            self.fieldAvgCount = statistics.mean(obj.count for obj in g3)
        else:
            self.fieldAvgCount = min((obj.count for obj in g3))

        self.valueUsedBytes = sum(obj.valueUsedBytes for obj in v1)
        self.valueAlignedBytes = sum(obj.valueAlignedBytes for obj in v2)
        self.total = sum(obj.total for obj in v3)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class Set(object):
    def __init__(self, redis):
        """
        :param RmaRedis redis:
        :return:
        """
        self.redis = redis

    def analyze(self, keys):
        key_stat = {
            'headers': ['Match', "Count", "Avg Count", "Value mem", "Real", "Ratio", "System*", "Encoding", "Total"],
            'data': []
        }
        # Undone Prefered encoding
        for pattern, data in keys.items():
            agg = SetAggregator((SetStatEntry(x, self.redis) for x in data), len(data))

            stat_entry = [
                pattern,
                len(data),
                agg.fieldAvgCount,
                agg.valueUsedBytes,
                agg.valueAlignedBytes,
                agg.valueAlignedBytes / (agg.valueUsedBytes if agg.valueUsedBytes > 0 else 1),
                agg.system,
                agg.encoding,
                agg.total
            ]

            key_stat['data'].append(stat_entry)

        key_stat['data'].sort(key=lambda x: x[8], reverse=True)
        key_stat['data'].append(make_total_row(key_stat['data'], ['Total:', sum, 0, sum, sum, 0, sum, '', sum]))

        return [
            "SET stat",
            key_stat
        ]
