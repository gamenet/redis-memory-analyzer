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

        keys_ = [
            ["Total keys in db", total_keys],
            ["RedisDB key space overhead", dict_overhead(total_keys)]
        ]
        try:
            keys_ += [["Used `{0}`".format(key), value] for key, value in self.redis.config_get("*max-*-*").items()]
        except ResponseError as e:
            self.logger.warning("*max* option skipped: {0}".format(repr(e)))

        keys_ += [["Info `{0}`".format(key), value] for key, value in self.redis.info('memory').items()]

        return [
            {
                'headers': ['Stat', "Value"],
                'data': keys_
            }
        ]
