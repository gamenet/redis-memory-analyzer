from redis import StrictRedis
from rma.jemalloc import *

size_of_pointer = 8
new_sds = False
allocator = Jemalloc

# Const
REDIS_SHARED_INTEGERS = 10000
REDIS_ENCODING_EMBSTR_SIZE_LIMIT = 39


# String encodings
REDIS_ENCODING_INT = 'int'
REDIS_ENCODING_EMBSTR = 'embstr'
REDIS_ENCODING_RAW = 'raw'

# Internal type mapping
REDIS_TYPE_ID_UNKNOWN = -1
REDIS_TYPE_ID_STRING = 0
REDIS_TYPE_ID_HASH = 1
REDIS_TYPE_ID_LIST = 2
REDIS_TYPE_ID_SET = 3
REDIS_TYPE_ID_ZSET = 4


def redis_type_to_id(key_type):
    """
    Convert redis type string to internal num type
    :param str key_type:
    :return int:
    """
    if key_type == b'string':
        return REDIS_TYPE_ID_STRING
    elif key_type == b'hash':
        return REDIS_TYPE_ID_HASH
    elif key_type == b'list':
        return REDIS_TYPE_ID_LIST
    elif key_type == b'set':
        return REDIS_TYPE_ID_SET
    elif key_type == b'zset':
        return REDIS_TYPE_ID_ZSET
    else:
        return REDIS_TYPE_ID_UNKNOWN


def type_id_to_redis_type(type_id):
    """
    Convert internal type id to Redis string type
    :param int type_id:
    :return str:
    """
    if type_id == REDIS_TYPE_ID_STRING:
        return 'string'
    elif type_id == REDIS_TYPE_ID_HASH:
        return 'hash'
    elif type_id == REDIS_TYPE_ID_LIST:
        return 'list'
    elif type_id == REDIS_TYPE_ID_SET:
        return 'set'
    elif type_id == REDIS_TYPE_ID_ZSET:
        return 'zset'
    else:
        return 'unknown'


def size_of_pointer_fn():
    """
    Return pointer size for current Redis connection
    :return int:
    """
    # UNDONE
    return 8


def get_redis_object_overhead():
    """
    See struct sdshdr over here https://github.com/antirez/redis/blob/unstable/src/sds.h:
    typedef struct redisObject {
        unsigned type:4;
        unsigned encoding:4;
        unsigned lru:REDIS_LRU_BITS; /* lru time (relative to server.lruclock) */
        int refcount;
        void *ptr;
    } robj;

    :param length:
    :return:
    """
    return 4 + 4 + 8 + 8 + size_of_pointer_fn()


def get_string_encoding(value):
    if is_num(value):
        return REDIS_ENCODING_INT
    elif len(value) < REDIS_ENCODING_EMBSTR_SIZE_LIMIT:
        return REDIS_ENCODING_EMBSTR
    else:
        return REDIS_ENCODING_RAW


def size_of_sds_string(value, encoding=REDIS_ENCODING_INT):
    if encoding == REDIS_ENCODING_INT:
        try:
            num_value = int(value)
            if num_value < REDIS_SHARED_INTEGERS:
                return 0
            else:
                return size_of_pointer_fn()
        except ValueError:
            pass

    return 8 + len(value) + 1


def size_of_aligned_string(value, encoding=""):
    if encoding == "":
        encoding = get_string_encoding(value)

    str_len = size_of_sds_string(value, encoding)
    return size_of_aligned_string_by_size(str_len, encoding)



def size_of_aligned_string_by_size(sdslen, encoding):
    r_obj = get_redis_object_overhead()
    if encoding == REDIS_ENCODING_INT:
        return allocator.align(r_obj)
    elif encoding == REDIS_ENCODING_EMBSTR:
        return allocator.align(sdslen + r_obj)
    else:
        return allocator.align(sdslen) + allocator.align(r_obj)


def dict_overhead(size):
    return Jemalloc.align(56 + 2*size_of_pointer_fn() + next_power_of_2(size) * dict_entry_overhead())


def dict_entry_overhead():
    return 3*size_of_pointer_fn()


def ziplist_overhead(size):
    return Jemalloc.align(12 + 21 * size)


def size_of_ziplist_aligned_string(value):
    # Looks like we need something more complex here. We use calculation as 21 bytes per entry + len of string
    # or len of pointer. Redis use more RAM saving policy but after aligning it has infelicity ~3-5%
    try:
        num_value = int(value)
        return Jemalloc.align(size_of_pointer_fn())
    except ValueError:
        pass

    return Jemalloc.align(len(value))


def linkedlist_overhead():
    # A list has 5 pointers + an unsigned long
    return 8 + 5*size_of_pointer_fn()

def linkedlist_entry_overhead():
    # See https://github.com/antirez/redis/blob/unstable/src/adlist.h
    # A node has 3 pointers
    return 3*size_of_pointer_fn()


def size_of_linkedlist_aligned_string(value):
    return Jemalloc.align(linkedlist_entry_overhead() + len(value))

class StringEntry:
    def __init__(self, value=""):
        self.encoding = get_string_encoding(value)
        self.useful_bytes = len(value)
        self.free_bytes = 0
        self.aligned = size_of_aligned_string(value, encoding=self.encoding)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


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
        try:
            self.encoding = redis.object("ENCODING", key_name).decode('utf8')
        except AttributeError as e:
            print(e, key_name)
            self.encoding = REDIS_ENCODING_EMBSTR

        if self.encoding == REDIS_ENCODING_INT:
            self.useful_bytes = self.get_int_encoded_bytes(redis, key_name)
            self.free_bytes = 0
            self.aligned = size_of_aligned_string_by_size(self.useful_bytes, encoding=self.encoding)
        elif self.encoding == REDIS_ENCODING_EMBSTR or self.encoding == REDIS_ENCODING_RAW:
            sdslen_response = redis.debug_sdslen(key_name)
            self.useful_bytes = sdslen_response['val_sds_len']
            self.free_bytes = sdslen_response['val_sds_avail']
            sds_len = 8 + self.useful_bytes + self.free_bytes + 1
            self.aligned = size_of_aligned_string_by_size(sds_len, encoding=self.encoding)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


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
