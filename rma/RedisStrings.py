from rma.StringStatisticEntry import *
from rma.Redis import *
from rma.Jemalloc import *

import codecs

class RedisStrings:
    key = "string"

    def overhead(self, str, encoding):
        return get_redis_object_overhead()

    def collect(self, redis, key):
        """
        :param redis:
        :type redis: RmaRedis
        :param key:
        :type key: str
        :return:
        """
        encoding = redis.object("ENCODING", key).decode('utf8')

        key_stat = StringStatisticEntry(r_obj=self.overhead(key, encoding), value=key)
        val_stat = StringStatisticEntry(r_obj=self.overhead(key, encoding), encoding=encoding)

        if encoding == REDIS_ENCODING_INT:
            key_stat.usedBytes = len(key)
            val_stat.usedBytes = size_of_pointer
            val_stat.aligned = size_of_pointer
        elif encoding == REDIS_ENCODING_EMBSTR or encoding == REDIS_ENCODING_RAW:
            sdslen_res = redis.debug_sdslen(key)

            # Inspection about zlib
            # zlib = codecs.encode(redis.get(key), "zlib")
            # print(len(zlib), sdslen_res['val_sds_len'])

            key_stat.usedBytes = sdslen_res['key_sds_len']
            key_stat.freeBytes = sdslen_res['key_sds_avail']
            val_stat.usedBytes = sdslen_res['val_sds_len']
            val_stat.freeBytes = sdslen_res['val_sds_avail']

            if encoding == REDIS_ENCODING_RAW:
                val_stat.aligned = Jemalloc.align(val_stat.total) + Jemalloc.align(val_stat.rObj)
            else:
                val_stat.aligned = Jemalloc.align(val_stat.total + val_stat.rObj)
        else:
            raise Exception("Unknown string encoding " + encoding, key)

        if key_stat.usedBytes == 0:
            raise Exception("Ups! " + encoding, key)

        key_stat.aligned = Jemalloc.align(key_stat.total + key_stat.rObj)
        return {'key': key_stat, 'value': val_stat}