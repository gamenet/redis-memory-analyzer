import statistics
from rma.redis import *
from rma.helpers import *
from redis.exceptions import RedisError


class RealStringEntry:
    def get_int_encoded_bytes(self, redis, key_name):
        try:
            num_value = int(redis.get(key_name))
            if num_value < REDIS_SHARED_INTEGERS:
                return 0
            else:
                return size_of_pointer_fn()
        except ValueError:
            pass

        return size_of_pointer_fn()

    def __init__(self, key_name, redis):
        """
        :param key_name:
        :param RmaRedis redis:
        :return:
        """

        self.logger = logging.getLogger(__name__)
        try:
            self.encoding = redis.object("ENCODING", key_name).decode('utf8')
        except AttributeError as e:
            self.logger.warning("Invalid encoding from server for key `%s` (would be skipped)" % key_name)
            self.encoding = REDIS_ENCODING_EMBSTR
            self.useful_bytes = 0
            self.free_bytes = 0
            self.aligned = 0
            return

        if self.encoding == REDIS_ENCODING_INT:
            self.useful_bytes = self.get_int_encoded_bytes(redis, key_name)
            self.free_bytes = 0
            self.aligned = size_of_aligned_string_by_size(self.useful_bytes, encoding=self.encoding)
        elif self.encoding == REDIS_ENCODING_EMBSTR or self.encoding == REDIS_ENCODING_RAW:
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


class ValueString:
    def __init__(self, redis):
        self.redis = redis
        self.logger = logging.getLogger(__name__)

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

            for key_name in data:
                try:
                    with RealStringEntry(key_name=key_name, redis=self.redis) as stat:
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
            prefered_encoding = pref_encoding(encodings)

            min_bytes = min(used_bytes)
            mean = statistics.mean(used_bytes) if total_elements > 1 else min_bytes

            stat_entry = [
                pattern,
                total_elements,
                used_user,
                free_user,
                aligned,
                aligned / (used_user if used_user > 0 else 1),
                prefered_encoding,
                min_bytes,
                max(used_bytes),
                mean,
            ]
            key_stat['data'].append(stat_entry)

        key_stat['data'].sort(key=lambda e: e[1], reverse=True)
        key_stat['data'].append(make_total_row(key_stat['data'], ['Total:', sum, sum, 0, sum, 0, '', 0, 0, 0]))

        return [
            "String value stat",
            key_stat
        ]
