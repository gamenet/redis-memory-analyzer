REDIS_ENCODING_ID_RAW = 0
REDIS_ENCODING_ID_INT = 1
REDIS_ENCODING_ID_EMBSTR = 2
REDIS_ENCODING_ID_HASHTABLE = 3
REDIS_ENCODING_ID_ZIPLIST = 4
REDIS_ENCODING_ID_LINKEDLIST = 5
REDIS_ENCODING_ID_QUICKLIST =6
REDIS_ENCODING_ID_INTSET = 7
REDIS_ENCODING_ID_SKIPLIST = 8

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
