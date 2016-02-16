import statistics
import logging
from tqdm import tqdm
from rma.redis import *
from rma.helpers import pref_encoding, make_total_row, progress_iterator
from redis.exceptions import RedisError


class RealStringEntry(object):
    @staticmethod
    def get_int_encoded_bytes(redis, key_name):
        try:
            num_value = int(redis.get(key_name))
            if num_value < REDIS_SHARED_INTEGERS:
                return 0
            else:
                return size_of_pointer_fn()
        except ValueError:
            pass

        return size_of_pointer_fn()

    def __init__(self, redis, info):
        """
        :param key_name:
        :param RmaRedis redis:
        :return:
        """
        key_name = info["name"]
        self.encoding = info["encoding"]
        self.logger = logging.getLogger(__name__)

        if self.encoding == REDIS_ENCODING_ID_INT:
            self.useful_bytes = self.get_int_encoded_bytes(redis, key_name)
            self.free_bytes = 0
            self.aligned = size_of_aligned_string_by_size(self.useful_bytes, encoding=self.encoding)
        elif self.encoding == REDIS_ENCODING_ID_EMBSTR or self.encoding == REDIS_ENCODING_ID_RAW:
            sdslen_response = redis.debug_sdslen(key_name)
            self.useful_bytes = sdslen_response['val_sds_len']
            self.free_bytes = sdslen_response['val_sds_avail']
            # INFO Rewrite this to support Redis >= 3.2 sds dynamic header
            sds_len = 8 + self.useful_bytes + self.free_bytes + 1
            self.aligned = size_of_aligned_string_by_size(sds_len, encoding=self.encoding)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class ValueString(object):
    def __init__(self, redis):
        self.redis = redis
        self.logger = logging.getLogger(__name__)

    def analyze(self, keys, total=0):
        key_stat = {
            'headers': ['Match', "Count", "Useful", "Free", "Real", "Ratio", "Encoding", "Min", "Max", "Avg"],
            'data': []
        }

        progress = tqdm(total=total,
                        mininterval=1,
                        desc="Processing String patterns",
                        leave=False)

        for pattern, data in keys.items():
            used_bytes = []
            free_bytes = []
            aligned_bytes = []
            encodings = []

            for key_info in progress_iterator(data, progress):
                try:
                    with RealStringEntry(redis=self.redis, info=key_info) as stat:
                        used_bytes.append(stat.useful_bytes)
                        free_bytes.append(stat.free_bytes)
                        aligned_bytes.append(stat.aligned)
                        encodings.append(stat.encoding)
                except RedisError as e:
                    # This code works in real time so key me be deleted and this code fail
                    self.logger.warning(repr(e))

            total_elements = len(used_bytes)
            used_user = sum(used_bytes)
            free_user = sum(free_bytes)
            aligned = sum(aligned_bytes)
            preferred_encoding = pref_encoding(encodings, redis_encoding_id_to_str)

            min_bytes = min(used_bytes)
            mean = statistics.mean(used_bytes) if total_elements > 1 else min_bytes

            stat_entry = [
                pattern,
                total_elements,
                used_user,
                free_user,
                aligned,
                aligned / (used_user if used_user > 0 else 1),
                preferred_encoding,
                min_bytes,
                max(used_bytes),
                mean,
            ]
            key_stat['data'].append(stat_entry)

        key_stat['data'].sort(key=lambda e: e[1], reverse=True)
        key_stat['data'].append(make_total_row(key_stat['data'], ['Total:', sum, sum, 0, sum, 0, '', 0, 0, 0]))

        progress.close()

        return [
            "String value stat",
            key_stat
        ]
