import logging
from redis import StrictRedis
from rma.jemalloc import *
from rma.redis_types import *


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

    :return:
    """
    return 4 + 4 + 8 + 8 + size_of_pointer_fn()


def get_string_encoding(value):
    if is_num(value):
        return REDIS_ENCODING_ID_INT
    elif len(value) < REDIS_ENCODING_EMBSTR_SIZE_LIMIT:
        return REDIS_ENCODING_ID_EMBSTR
    else:
        return REDIS_ENCODING_ID_RAW


def size_of_sds_string(value, encoding=REDIS_ENCODING_ID_INT):
    if encoding == REDIS_ENCODING_ID_INT:
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
    if encoding == REDIS_ENCODING_ID_INT:
        return allocator.align(r_obj)
    elif encoding == REDIS_ENCODING_ID_EMBSTR:
        return allocator.align(sdslen + r_obj)
    else:
        # REDIS_ENCODING_ID_RAW
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


def intset_overhead(size):
    #     typedef struct intset {
    #     uint32_t encoding;
    #     uint32_t length;
    #     int8_t contents[];
    # } intset;
    return (4 + 4) * size


def intset_aligned(value):
    overhead = intset_overhead(1)
    try:
        val = int(value)

    except ValueError:
        return Jemalloc.align(8 + overhead)

    if val < 65535:
        return Jemalloc.align(2 + overhead)

    if val < 2147483647:
        return Jemalloc.align(4 + overhead)

    return Jemalloc.align(8 + overhead)


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
