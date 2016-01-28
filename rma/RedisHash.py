from rma.StringStatisticEntry import *
from rma.Redis import *
from rma.Jemalloc import *

import codecs

class RedisHash:
    key = "hash"

    def overhead(self, str, encoding):
        return get_redis_object_overhead()

    def collect(self, redis, key):
        """

        :param RmaRedis redis:
        :param key:
        :return:
        """
        encoding = redis.object("ENCODING", key).decode('utf8')

        key_stat = StringStatisticEntry(r_obj=self.overhead(key, encoding), value=key)
        val_stat = StringStatisticEntry(r_obj=self.overhead(key, encoding), encoding=encoding)


        # Количество полей
        # Кодировка
        # Длина ключа
        # Длина значения
        # Память под ключи
        # Память под значения


        return {'key': key_stat, 'value': val_stat}