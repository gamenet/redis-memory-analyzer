from rma.Redis import *

class GlobalKeySpace:
    def __init__(self, redis):
        """
        :param RmaRedis redis:
        :return:
        """
        self.redis = redis

    def analyze(self, keys=[]):
        total_keys = self.redis.total_keys()
        return [
            {
                'headers': ['Stat', "Value"],
                'data': [
                    ["Total keys in db", total_keys],
                    ["RedisDB key space overhead", dict_overhead(total_keys)]
                ]
            }
        ]
