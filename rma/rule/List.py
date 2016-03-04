import statistics
from itertools import tee
from tqdm import tqdm
from rma.redis import *
from rma.helpers import pref_encoding, make_total_row, progress_iterator


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
        import time
        time.sleep(0.001)
        used_bytes_iter, min_iter, max_iter = tee((len(x) for x in self.values), 3)

        if self.encoding == REDIS_ENCODING_ID_LINKEDLIST:
            self.system = dict_overhead(self.count)
            self.valueAlignedBytes = sum(map(size_of_linkedlist_aligned_string, self.values))
        elif self.encoding == REDIS_ENCODING_ID_ZIPLIST or self.encoding == REDIS_ENCODING_ID_QUICKLIST:
            # Undone `quicklist`
            self.system = ziplist_overhead(self.count)
            self.valueAlignedBytes = sum(map(size_of_ziplist_aligned_string, self.values))
        else:
            raise Exception('Panic', 'Unknown encoding %s in %s' % (self.encoding, key_name))

        self.valueUsedBytes = sum(used_bytes_iter)

        if self.count > 0:
            self.valueMin = min(min_iter)
            self.valueMax = max(max_iter)
        else:
            self.valueMin = 0
            self.valueMax = 0


class ListAggregator(object):
    def __init__(self, all_obj, total):
        self.total_elements = total

        encode_iter, sys_iter, avg_iter, stdev_iter, min_iter, max_iter, value_used_iter, value_align_iter = \
            tee(all_obj, 8)

        self.encoding = pref_encoding([obj.encoding for obj in encode_iter], redis_encoding_id_to_str)
        self.system = sum(obj.system for obj in sys_iter)

        if total == 0:
            self.fieldAvgCount = 0
            self.fieldStdev = 0
            self.fieldMinCount = 0
            self.fieldMaxCount = 0
        elif total > 1:
            self.fieldAvgCount = statistics.mean(obj.count for obj in avg_iter)
            self.fieldStdev = statistics.stdev(obj.count for obj in stdev_iter)
            self.fieldMinCount = min((obj.count for obj in min_iter))
            self.fieldMaxCount = max((obj.count for obj in max_iter))
        else:
            self.fieldAvgCount = min((obj.count for obj in avg_iter))
            self.fieldStdev = 0
            self.fieldMinCount = self.fieldAvgCount
            self.fieldMaxCount = self.fieldAvgCount

        self.valueUsedBytes = sum(obj.valueUsedBytes for obj in value_used_iter)
        self.valueAlignedBytes = sum(obj.valueAlignedBytes for obj in value_align_iter)

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

    def analyze(self, keys, total=0):
        key_stat = {
            'headers': ['Match', "Count", "Avg Count", "Min Count", "Max Count", "Stdev Count", "Value mem", "Real", "Ratio", "System", "Encoding", "Total"],
            'data': []
        }

        progress = tqdm(total=total,
                        mininterval=1,
                        desc="Processing List patterns",
                        leave=False)

        for pattern, data in keys.items():
            agg = ListAggregator(progress_iterator((ListStatEntry(x, self.redis) for x in data), progress), len(data))

            stat_entry = [
                pattern,
                len(data),
                agg.fieldAvgCount,
                agg.fieldMinCount,
                agg.fieldMaxCount,
                agg.fieldStdev,
                agg.valueUsedBytes,
                agg.valueAlignedBytes,
                agg.valueAlignedBytes / (agg.valueUsedBytes if agg.valueUsedBytes > 0 else 1),
                agg.system,
                agg.encoding,
                agg.valueAlignedBytes + agg.system
            ]

            key_stat['data'].append(stat_entry)
            progress.update()

        key_stat['data'].sort(key=lambda x: x[8], reverse=True)
        key_stat['data'].append(make_total_row(key_stat['data'], ['Total:', sum, 0, 0, 0, 0, sum, sum, 0, sum, '', sum]))

        progress.close()
        return [
            "List stat",
            key_stat
        ]
