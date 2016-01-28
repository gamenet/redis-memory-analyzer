from redis import StrictRedis

REDIS_TYPE_STRING = 'string'
REDIS_TYPE_HASH = 'hash'
REDIS_TYPE_SET = 'set'

REDIS_ENCODING_INT = 'int'
REDIS_ENCODING_EMBSTR = 'embstr'
REDIS_ENCODING_RAW = 'raw'

REDIS_ENCODING_EMBSTR_SIZE_LIMIT = 39

size_of_pointer = 8


def parse_debug(response):
    """
    Parse the result of Redis's DEBUG command into a Python dict
    :param bytearray response:
    :return disc:
    """
    info = {}
    response = response.decode('utf8')

    for line in response.split(','):
        if line.find(':') != -1:
            key, value = line.split(':', 1)
            info[key.strip()] = int(value)
        else:
            # if the line isn't splittable, append it to the "__raw__" key
            info.setdefault('__raw__', []).append(line)

    return info


class RmaRedis(StrictRedis):
    def debug_sdslen(self, key):
        return parse_debug(self.execute_command("DEBUG SDSLEN", key))

    def total_keys(self):
        return self.info('keyspace')['db0']['keys']
