import logging
from rma.redis import dict_overhead
from redis.exceptions import ResponseError


class GlobalKeySpace(object):
    def __init__(self, redis):
        """
        :param RmaRedis redis:
        :return:
        """
        self.redis = redis
        self.logger = logging.getLogger(__name__)

    def analyze(self):
        total_keys = self.redis.dbsize()
        used = {}
        info = {}

        try:
            for key, value in self.redis.config_get("*max-*-*").items():
                used[key] = value
        except ResponseError as e:
            self.logger.warning("*max* option skipped: %s", repr(e))

        for key, value in self.redis.info('memory').items():
            info[key] = value

        return {
            "info": info,
            "used": used,
            "totalKeys": total_keys,
            "redisKeySpaceOverhead": dict_overhead(total_keys),
        }
