from rma.Redis import *
from rma.RedisStrings import RedisStrings
from rma.RedisHash import RedisHash
from rma.Splitter import Splitter

class Scanner:
    match = '*'
    analyzers = {
        REDIS_TYPE_STRING: RedisStrings(),
        REDIS_TYPE_HASH: RedisHash(),
    }

    def __init__(self, r, match="*"):
        """
        :param RmaRedis r:
        :param str match:
        :return:
        """

        self.r = r
        self.match = match

    def scan(self, callback=None, limit=1000):
        total = 0
        res = dict(string=[], hash=[])
        for key in self.r.scan_iter(self.match, count=1000):
            key_type = self.r.type(key).decode("utf-8")

            if callback:
                callback(key)

            if key_type in self.analyzers:
                res[key_type].append(self.analyzers[key_type].collect(redis=self.r, key=key.decode('utf8')))
                continue

            total += 1
            if total > limit:
                break

        splitter = Splitter()
        result = splitter.split(map(lambda x: x['key'].value.split(':'), res["string"]))

        return dict(strings=dict(stat=res["string"], patterns=result))
