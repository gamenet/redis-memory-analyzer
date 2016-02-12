from rma.redis import *
from itertools import tee
from rma.helpers import *

import statistics


class ListStatEntry(object):
    def __init__(self, info, redis):
        """
        :param key_name:
        :param RmaRedis redis:
        :return:
        """
        key_name = info["name"]
        self.encoding = info['encoding']

        self.values = redis.lrange(key_name, 0, -1)
        self.count = len(self.values)

        m, m2, m3 = tee((len(x) for x in self.values), 3)

        if self.encoding == REDIS_ENCODING_ID_LINKEDLIST:
            self.system = dict_overhead(self.count)
            self.valueAlignedBytes = sum(map(size_of_linkedlist_aligned_string, self.values))
        elif self.encoding == REDIS_ENCODING_ID_ZIPLIST or self.encoding == REDIS_ENCODING_ID_QUICKLIST:
            # Undone `quicklist`
            self.system = ziplist_overhead(self.count)
            self.valueAlignedBytes = sum(map(size_of_ziplist_aligned_string, self.values))
        else:
            raise Exception('Panic', 'Unknown encoding %s in %s' % (self.encoding, key_name))

        self.valueUsedBytes = sum(m)
        self.valueMin = min(m2)
        self.valueMax = max(m3)


class ListAggregator(object):
    def __init__(self, all_obj, total):
        self.total_elements = total

        g00, g0, g1, g2, g3, g4, v1, v2 = tee(all_obj, 8)

        self.encoding = pref_encoding([obj.encoding for obj in g00], redis_encoding_id_to_str)
        self.system = sum(obj.system for obj in g0)
        if total > 1:
            self.fieldAvgCount = statistics.mean(obj.count for obj in g3)
        else:
            self.fieldAvgCount = min((obj.count for obj in g3))

        self.valueUsedBytes = sum(obj.valueUsedBytes for obj in v1)
        self.valueAlignedBytes = sum(obj.valueAlignedBytes for obj in v2)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class List(object):
    def __init__(self, redis):
        """
        :param RmaRedis redis:
        :return:
        """
        self.redis = redis

    def analyze(self, keys):
        key_stat = {
            'headers': ['Match', "Count", "Avg Count", "Value mem", "Real", "Ratio", "System", "Encoding", "Total"],
            'data': []
        }
        # Undone Prefered encoding
        for pattern, data in keys.items():
            agg = ListAggregator((ListStatEntry(x, self.redis) for x in data), len(data))

            stat_entry = [
                pattern,
                len(data),
                agg.fieldAvgCount,
                agg.valueUsedBytes,
                agg.valueAlignedBytes,
                agg.valueAlignedBytes / (agg.valueUsedBytes if agg.valueUsedBytes > 0 else 1),
                agg.system,
                agg.encoding,
                agg.valueAlignedBytes + agg.system
            ]

            key_stat['data'].append(stat_entry)

        key_stat['data'].sort(key=lambda x: x[8], reverse=True)
        key_stat['data'].append(make_total_row(key_stat['data'], ['Total:', sum, 0, sum, sum, 0, sum, '', sum]))

        return [
            "List stat",
            key_stat
        ]
