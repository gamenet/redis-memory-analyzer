from rma.redis import *
from itertools import tee
from rma.helpers import *

import statistics


class HashStatEntry:
    def __init__(self, key_name, redis):
        """
        :param key_name:
        :param RmaRedis redis:
        :return:
        """
        self.keys = []
        self.values = []
        self.encoding = redis.object('encoding', key_name).decode('utf8')

        for key, value in redis.hscan_iter(key_name, '*'):
            self.keys.append(key)
            self.values.append(value)

        self.count = len(self.keys)

        args, args2, args3, args4, args5 = tee((len(x) for x in self.keys), 5)
        m, m2, m3, m4, m5 = tee((len(x) for x in self.values), 5)

        self.fieldUsedBytes = sum(args)
        if self.encoding == 'hashtable':
            self.system = dict_overhead(self.count)
            self.fieldAlignedBytes = sum(map(size_of_aligned_string, self.keys))
            self.valueAlignedBytes = sum(map(size_of_aligned_string, self.values))
        elif self.encoding =='ziplist':
            self.system = ziplist_overhead(self.count)
            self.fieldAlignedBytes = sum(map(size_of_ziplist_aligned_string, self.keys))
            self.valueAlignedBytes = sum(map(size_of_ziplist_aligned_string, self.values))
        else:
            raise Exception('Panic', 'Unknown encoding %s in %s' % (self.encoding, key_name))

        self.valueUsedBytes = sum(m)
        self.fieldMin = min(args2)
        self.fieldMax = max(args3)
        self.valueMin = min(m2)
        self.valueMax = max(m3)


class HashAggreegator:
    def __init__(self, all_obj, total):
        self.total_elements = total

        g00, g0, g1, g2, g3, g4, v1, v2 = tee(all_obj, 8)

        self.encoding = pref_encoding([obj.encoding for obj in g00])
        self.system = sum(obj.system for obj in g0)
        self.fieldUsedBytes = sum(obj.fieldUsedBytes for obj in g1)
        self.fieldAlignedBytes = sum(obj.fieldAlignedBytes for obj in g2)

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


class Hash:
    def __init__(self, redis):
        """
        :param RmaRedis redis:
        :return:
        """
        self.redis = redis

    def analyze(self, keys):
        key_stat = {
            'headers': ['Match', "Count", "Avg key count", "Key mem", "Real", "Ratio", "Value mem", "Real", "Ratio", "System", "Encoding", "Total mem","Total aligned" ],
            'data': []
        }
        # Undone Prefered encoding
        for pattern, data in keys.items():
            agg = HashAggreegator((HashStatEntry(x, self.redis) for x in data), len(data))

            stat_entry = [
                pattern,
                len(data),
                agg.fieldAvgCount,
                agg.fieldUsedBytes,
                agg.fieldAlignedBytes,
                agg.fieldAlignedBytes / agg.fieldUsedBytes,
                agg.valueUsedBytes,
                agg.valueAlignedBytes,
                agg.valueAlignedBytes/ (agg.valueUsedBytes if agg.valueUsedBytes > 0 else 1),
                agg.system,
                agg.encoding,
                agg.fieldUsedBytes + agg.valueUsedBytes,
                agg.fieldAlignedBytes + agg.valueAlignedBytes + agg.system,
            ]

            key_stat['data'].append(stat_entry)

        key_stat['data'].sort(key=lambda x: x[12], reverse=True)
        key_stat['data'].append(make_total_row(key_stat['data'], ['Total:', sum, 0, sum, sum, 0, sum, sum, 0, sum, '', sum, sum]))

        return [
            "Hash stat",
            key_stat
        ]
