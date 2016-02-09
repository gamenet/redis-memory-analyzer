from rma.redis import *


class GlobalKeySpace:
    def __init__(self, redis):
        """
        :param RmaRedis redis:
        :return:
        """
        self.redis = redis

    def analyze(self, keys=None):
        total_keys = self.redis.total_keys()

        keys_ = [
            ["Total keys in db", total_keys],
            ["RedisDB key space overhead", dict_overhead(total_keys)]
        ]
        keys_ += [["Used `{0}`".format(key), value] for key, value in self.redis.config_get("*max-*-*").items()]
        keys_ += [["Info `{0}`".format(key), value] for key, value in self.redis.info('memory').items()]

        return [
            {
                'headers': ['Stat', "Value"],
                'data': keys_
            }
        ]
