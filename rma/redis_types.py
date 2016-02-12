# Internal encoding mapping
REDIS_ENCODING_ID_RAW = 0
REDIS_ENCODING_ID_INT = 1
REDIS_ENCODING_ID_EMBSTR = 2
REDIS_ENCODING_ID_HASHTABLE = 3
REDIS_ENCODING_ID_ZIPLIST = 4
REDIS_ENCODING_ID_LINKEDLIST = 5
REDIS_ENCODING_ID_QUICKLIST =6
REDIS_ENCODING_ID_INTSET = 7
REDIS_ENCODING_ID_SKIPLIST = 8
REDIS_ENCODING_ID_ALL = [
    REDIS_ENCODING_ID_RAW,
    REDIS_ENCODING_ID_INT,
    REDIS_ENCODING_ID_EMBSTR,
    REDIS_ENCODING_ID_HASHTABLE,
    REDIS_ENCODING_ID_ZIPLIST,
    REDIS_ENCODING_ID_LINKEDLIST,
    REDIS_ENCODING_ID_QUICKLIST,
    REDIS_ENCODING_ID_INTSET,
    REDIS_ENCODING_ID_SKIPLIST
]

# Internal type mapping
REDIS_TYPE_ID_UNKNOWN = -1
REDIS_TYPE_ID_STRING = 0
REDIS_TYPE_ID_HASH = 1
REDIS_TYPE_ID_LIST = 2
REDIS_TYPE_ID_SET = 3
REDIS_TYPE_ID_ZSET = 4
REDIS_TYPE_ID_ALL = [
    REDIS_TYPE_ID_STRING,
    REDIS_TYPE_ID_HASH,
    REDIS_TYPE_ID_LIST,
    REDIS_TYPE_ID_SET,
    REDIS_TYPE_ID_ZSET
]

REDIS_ENCODING_STR_TO_ID_LIB = {
    b'raw': REDIS_ENCODING_ID_RAW,
    b'int': REDIS_ENCODING_ID_INT,
    b'embstr': REDIS_ENCODING_ID_EMBSTR,
    b'hashtable': REDIS_ENCODING_ID_HASHTABLE,
    b'ziplist': REDIS_ENCODING_ID_ZIPLIST,
    b'linkedlist': REDIS_ENCODING_ID_LINKEDLIST,
    b'quicklist': REDIS_ENCODING_ID_QUICKLIST,
    b'intset': REDIS_ENCODING_ID_INTSET,
    b'skiplist': REDIS_ENCODING_ID_SKIPLIST,
}

REDIS_ENCODING_ID_TO_STR_LIB = dict((v, k) for k, v in REDIS_ENCODING_STR_TO_ID_LIB.items())


def redis_encoding_str_to_id(key_encoding):
    if key_encoding in REDIS_ENCODING_STR_TO_ID_LIB:
        return REDIS_ENCODING_STR_TO_ID_LIB[key_encoding]

    raise ValueError("Invalid encoding `%s` given" % key_encoding)


def redis_encoding_id_to_str(key_encoding):
    if key_encoding in REDIS_ENCODING_ID_TO_STR_LIB:
        return REDIS_ENCODING_ID_TO_STR_LIB[key_encoding].decode('utf8')

    raise ValueError("Invalid encoding `%s` given" % key_encoding)


def redis_type_to_id(key_type):
    """
    Convert redis type string to internal num type
    :param str key_type:
    :return int:
    """
    if key_type == b'string' or key_type == 'string':
        return REDIS_TYPE_ID_STRING
    elif key_type == b'hash' or key_type == 'hash':
        return REDIS_TYPE_ID_HASH
    elif key_type == b'list' or key_type == 'list':
        return REDIS_TYPE_ID_LIST
    elif key_type == b'set' or key_type == 'set':
        return REDIS_TYPE_ID_SET
    elif key_type == b'zset' or key_type == 'zset':
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