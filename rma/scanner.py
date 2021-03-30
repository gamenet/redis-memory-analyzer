import logging
import msgpack
from redis.exceptions import ResponseError
from tqdm import tqdm
from rma.redis import *


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


class Scanner(object):
    """
    Get all keys from Redis database with given match and limits. If limit specified would be retrieved not more then
    limit keys.
    """
    logger = logging.getLogger(__name__)

    def __init__(self, redis, match="*", accepted_types=None):
        """
        :param RmaRedis redis:
        :param str match: Wild card match supported in Redis SCAN command
        :return:
        """
        self.redis = redis
        self.match = match
        self.accepted_types = accepted_types[:] if accepted_types else REDIS_TYPE_ID_ALL
        self.pipeline_mode = False
        self.resolve_types_script = self.redis.register_script("""
            local ret = {}
            for i = 1, #KEYS do
                local type = redis.call("TYPE", KEYS[i])
                local encoding = redis.call("OBJECT", "ENCODING",KEYS[i])
                local ttl = redis.call("TTL", KEYS[i])
                ret[i] = {type["ok"], encoding, ttl}
            end
            return cmsgpack.pack(ret)
        """)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def batch_scan(self, count=1000, batch_size=3000):
        ret = []
        for key in self.redis.scan_iter(self.match, count=count):
            ret.append(key)
            if len(ret) == batch_size:
                yield from self.resolve_types(ret)

        if len(ret):
            yield from self.resolve_types(ret)

    def resolve_types(self, ret):
        if not self.pipeline_mode:
            try:
                key_with_types = msgpack.unpackb(self.resolve_types_script(ret))
            except ResponseError as e:
                if "CROSSSLOT" not in repr(e):
                    raise e
                key_with_types = self.resolve_with_pipe(ret)
                self.pipeline_mode = True
        else:
            key_with_types = self.resolve_with_pipe(ret)

        for i in range(0, len(ret)):
            yield key_with_types[i], ret[i]

        ret.clear()

    def resolve_with_pipe(self, ret):
        pipe = self.redis.pipeline(transaction=False)
        for key in ret:
            pipe.type(key)
            pipe.object('ENCODING', key)
            pipe.ttl(key)
        key_with_types = [{'type': x, 'encoding': y, 'ttl': z} for x, y, z in chunker(pipe.execute(), 3)]
        return key_with_types

    def scan(self, limit=1000):
        with tqdm(total=min(limit, self.redis.dbsize()), desc="Match {0}".format(self.match),
                  miniters=1000) as progress:

            total = 0
            for key_tuple in self.batch_scan():
                key_info, key_name = key_tuple

                if type(key_info) == list:
                    key_type, key_encoding, key_ttl = key_info
                else:
                    key_type = key_info["type"]
                    key_encoding = key_info["encoding"]
                    key_ttl = key_info["ttl"]

                if not key_name:
                    self.logger.warning(
                        '\r\nWarning! Scan iterator return key with empty name `` and type %s', key_type)
                    continue

                to_id = redis_type_to_id(key_type)
                if to_id in self.accepted_types:
                    key_info_obj = {
                        'name': key_name.decode("utf-8", "replace"),
                        'type': to_id,
                        'encoding': redis_encoding_str_to_id(key_encoding),
                        'ttl': key_ttl
                    }
                    yield key_info_obj

                progress.update()

                total += 1
                if total > limit:
                    logging.info("\r\nLimit %s reached", limit)
                    break
