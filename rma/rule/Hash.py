import statistics
from itertools import tee
from rma.redis import *
from rma.helpers import pref_encoding, make_total_row


class HashStatEntry(object):
    def __init__(self, info, redis):
        """
        :param key_name:
        :param RmaRedis redis:
        :return:
        """
        key_name = info['name']

        self.keys = []
        self.values = []
        self.encoding = info["encoding"]

        for key, value in redis.hscan_iter(key_name, '*'):
            self.keys.append(key)
            self.values.append(value)

        self.count = len(self.keys)

        args, args2, args3 = tee((len(x) for x in self.keys), 3)
        m, m2, m3 = tee((len(x) for x in self.values), 3)

        self.fieldUsedBytes = sum(args)
        if self.encoding == REDIS_ENCODING_ID_HASHTABLE:
            self.system = dict_overhead(self.count)
            self.fieldAlignedBytes = sum(map(size_of_aligned_string, self.keys))
            self.valueAlignedBytes = sum(map(size_of_aligned_string, self.values))
        elif self.encoding == REDIS_ENCODING_ID_ZIPLIST:
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


class HashAggregator(object):
    def __init__(self, all_obj, total):
        self.total_elements = total

        g00, g0, g1, g2, g3, v1, v2 = tee(all_obj, 7)

        self.encoding = pref_encoding([obj.encoding for obj in g00], redis_encoding_id_to_str)
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


class Hash(object):
    def __init__(self, redis):
        """
        :param RmaRedis redis:
        :return:
        """
        self.redis = redis

    def analyze(self, keys):
        key_stat = {
            'headers': ['Match', "Count", "Avg field count", "Key mem", "Real", "Ratio", "Value mem", "Real", "Ratio",
                        "System", "Encoding", "Total mem", "Total aligned"],
            'data': []
        }
        # Undone Prefered encoding
        for pattern, data in keys.items():
            agg = HashAggregator((HashStatEntry(x, self.redis) for x in data), len(data))

            stat_entry = [
                pattern,
                len(data),
                agg.fieldAvgCount,
                agg.fieldUsedBytes,
                agg.fieldAlignedBytes,
                agg.fieldAlignedBytes / agg.fieldUsedBytes,
                agg.valueUsedBytes,
                agg.valueAlignedBytes,
                agg.valueAlignedBytes / (agg.valueUsedBytes if agg.valueUsedBytes > 0 else 1),
                agg.system,
                agg.encoding,
                agg.fieldUsedBytes + agg.valueUsedBytes,
                agg.fieldAlignedBytes + agg.valueAlignedBytes + agg.system,
            ]

            key_stat['data'].append(stat_entry)

        key_stat['data'].sort(key=lambda x: x[12], reverse=True)
        key_stat['data'].append(
            make_total_row(key_stat['data'], ['Total:', sum, 0, sum, sum, 0, sum, sum, 0, sum, '', sum, sum]))

        return [
            "Hash stat",
            key_stat
        ]
